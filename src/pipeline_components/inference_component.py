"""
Inference component for generating predictions with the fine-tuned model.
"""
from kfp.dsl import component, Input, Output, Dataset, Model
from typing import Dict


@component(
    base_image="pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel",
    packages_to_install=[
        "transformers==4.46.0",
        "peft==0.13.2",
        "datasets==3.0.0",
        "accelerate==1.0.1",
        "bitsandbytes==0.43.3",
        "pandas==2.2.3",
        "gcsfs==2024.9.0",
        "google-cloud-storage==2.18.2",
    ],
)
def inference_component(
    fine_tuned_model: Input[Model],
    test_dataset: Input[Dataset],
    model_name: str,
    max_samples: int,
    predictions: Output[Dataset],
) -> Dict[str, int]:
    """Generate predictions using the fine-tuned model.
    
    Args:
        fine_tuned_model: Fine-tuned model with LoRA adapters
        test_dataset: Test dataset in JSON Lines format
        model_name: Base model name for tokenizer
        max_samples: Maximum number of samples to predict
        predictions: Output path for predictions CSV
        
    Returns:
        Dictionary with prediction statistics
    """
    import torch
    import pandas as pd
    import json
    import re
    import logging
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from datasets import load_dataset
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Loading base model: {model_name}")
    logger.info(f"Using device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    # Load LoRA adapter
    logger.info(f"Loading LoRA adapter from {fine_tuned_model.path}")
    model = PeftModel.from_pretrained(base_model, fine_tuned_model.path)
    model.eval()
    
    # Load test dataset
    logger.info(f"Loading test dataset from {test_dataset.path}")
    dataset = load_dataset("json", data_files=test_dataset.path, split="train")
    
    # Limit samples for evaluation
    num_samples = min(len(dataset), max_samples)
    logger.info(f"Generating predictions for {num_samples} samples")
    
    # Generate predictions
    results = []
    
    for i in range(num_samples):
        sample = dataset[i]
        messages = sample["messages"]
        
        # Extract user input and reference response
        user_input = messages[0]["content"]
        reference = messages[1]["content"]
        
        # Build prompt with chat template
        prompt_messages = [{"role": "user", "content": user_input}]
        prompt = tokenizer.apply_chat_template(
            prompt_messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        
        # Generate response
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Extract response (remove prompt and special tokens)
        # Pattern to extract assistant response
        pattern = r"<\|assistant\|>\s*(.*?)(?:<\|end\||$)"
        match = re.search(pattern, generated_text, re.DOTALL)
        
        if match:
            extracted_response = match.group(1).strip()
        else:
            # Fallback: remove the prompt part
            extracted_response = generated_text.replace(prompt, "").strip()
            # Remove remaining special tokens
            extracted_response = re.sub(r"<\|.*?\|>", "", extracted_response).strip()
        
        results.append({
            "user_input": user_input,
            "reference": reference,
            "extracted_response": extracted_response,
        })
        
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{num_samples} samples")
    
    # Save predictions as CSV
    df = pd.DataFrame(results)
    df.to_csv(predictions.path, index=False)
    logger.info(f"Saved predictions to {predictions.path}")
    
    # Log sample predictions
    logger.info("\nSample predictions:")
    for i in range(min(3, len(df))):
        logger.info(f"\n--- Sample {i+1} ---")
        logger.info(f"User: {df.iloc[i]['user_input']}")
        logger.info(f"Reference: {df.iloc[i]['reference']}")
        logger.info(f"Prediction: {df.iloc[i]['extracted_response']}")
    
    return {
        "total_predictions": len(results),
        "samples_processed": num_samples,
    }
