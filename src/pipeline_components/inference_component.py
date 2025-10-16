"""
Kubeflow Pipeline component for inference with fine-tuned Phi-3 model.
Takes fine-tuned model and test dataset, outputs predictions in ragas format.
"""

from kfp.dsl import component, InputPath, OutputPath
from typing import NamedTuple

@component(
    base_image="pytorch/pytorch:2.8.0-cuda12.9-cudnn9-devel",
    packages_to_install=[
        "transformers==4.46.3",
        "torch",
        "pandas==2.3.3",
        "datasets==4.2.0",
        "google-cloud-storage==2.19.0",
        "gcsfs==2025.9.0"
    ]
)
def inference_component(
    model_path: InputPath(str),
    test_dataset: InputPath(str),
    predictions_output_path: OutputPath(str),
    max_new_tokens: int = 50,
    temperature: float = 0.7,
    top_p: float = 0.9,
    num_samples: int = -1  # -1 means process all samples
) -> NamedTuple("InferenceOutput", [("num_predictions", int), ("avg_response_length", float)]):
    """
    Generate predictions using fine-tuned Phi-3 model on test dataset.
    
    Args:
        model_path (InputPath): Path to fine-tuned model directory
        test_dataset (InputPath): Path to test dataset in JSON format
        predictions_output_path (OutputPath): Path to save predictions CSV
        max_new_tokens (int): Maximum tokens to generate
        temperature (float): Sampling temperature
        top_p (float): Top-p sampling parameter
        num_samples (int): Number of samples to process (-1 for all)
        
    Returns:
        NamedTuple: Statistics about the inference run
    """
    import os
    import json
    import re
    import logging
    import pandas as pd
    import torch
    from typing import Any
    from google.cloud import storage
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Phi-3 inference component")
    logger.info(f"💾 CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"🎯 Device: {torch.cuda.get_device_name()}")
    
    def download_model(model_uri: str, local_dir: str):
        """Download model from GCS to local directory."""
        logger.info(f"📥 Downloading model from: {model_uri}")
        
        if not model_uri.startswith("gs://"):
            # Assume it's already a local path from the pipeline
            logger.info(f"📁 Using local model path: {model_uri}")
            return model_uri
        
        # Parse GCS URI
        path_parts = model_uri[5:].split('/', 1)
        bucket_name = path_parts[0]
        prefix = path_parts[1] if len(path_parts) > 1 else ""
        
        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Create local directory
        os.makedirs(local_dir, exist_ok=True)
        
        # Download all files
        blobs = bucket.list_blobs(prefix=prefix)
        downloaded_files = []
        
        for blob in blobs:
            if blob.name.endswith('/'):
                continue
                
            relative_path = blob.name[len(prefix):].lstrip('/')
            if not relative_path:
                continue
                
            local_file_path = os.path.join(local_dir, relative_path)
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            blob.download_to_filename(local_file_path)
            downloaded_files.append(local_file_path)
        
        logger.info(f"📦 Downloaded {len(downloaded_files)} files")
        return local_dir
    
    def build_prompt(tokenizer: AutoTokenizer, sentence: str):
        """Build a prompt from a sentence applying the chat template."""
        messages = [{"role": "user", "content": sentence}]
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        return prompt
    
    def generate_response(
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the model given a prompt."""
        generation_params = {
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_p": top_p,
            "pad_token_id": tokenizer.eos_token_id,
            "eos_token_id": tokenizer.eos_token_id,
        }
        generation_params.update(kwargs)
        
        inputs = tokenizer(prompt, return_tensors="pt")
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(**inputs, **generation_params)
        
        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return full_output
    
    def extract_response(model_output: str) -> str:
        """Extract the actual response from the model output."""
        pattern = r'<\|assistant\|\>\s*(.*?)(?:<\|end\|\>|$)'
        match = re.search(pattern, model_output, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        else:
            if '<|assistant|>' in model_output:
                parts = model_output.split('<|assistant|>')
                if len(parts) > 1:
                    response = parts[-1].strip()
                    response = re.sub(r'<\|end\|\>.*$', '', response, flags=re.DOTALL).strip()
                    return response
            
            logger.warning("Could not extract response from model output")
            return model_output
    
    # Step 1: Load model and tokenizer
    logger.info("🔄 Loading model and tokenizer...")
    
    # Download model if it's a GCS URI
    if isinstance(model_path, str) and model_path.startswith("gs://"):
        local_model_dir = "/tmp/downloaded_model"
        model_path = download_model(model_path, local_model_dir)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    logger.info(f"✅ Model loaded:")
    logger.info(f"  Device: {next(model.parameters()).device}")
    logger.info(f"  Data type: {next(model.parameters()).dtype}")
    
    # Step 2: Load test dataset
    logger.info(f"📂 Loading test dataset from: {test_dataset}")
    with open(test_dataset, 'r') as f:
        test_data = [json.loads(line) for line in f]
    
    logger.info(f"✅ Loaded {len(test_data)} test examples")
    
    # Extract sentences and references
    test_sentences = []
    test_references = []
    
    for row in test_data:
        messages = row['messages']
        user_msg = None
        assistant_msg = None
        
        for msg in messages:
            if msg['role'] == 'user':
                user_msg = msg['content']
            elif msg['role'] == 'assistant':
                assistant_msg = msg['content']
        
        if user_msg and assistant_msg:
            test_sentences.append(user_msg)
            test_references.append(assistant_msg)
    
    # Limit number of samples if specified
    if num_samples > 0 and num_samples < len(test_sentences):
        test_sentences = test_sentences[:num_samples]
        test_references = test_references[:num_samples]
        logger.info(f"🔢 Processing {num_samples} samples (limited)")
    
    logger.info(f"📊 Processing {len(test_sentences)} sentence pairs")
    
    # Step 3: Generate predictions
    logger.info("🚀 Starting inference...")
    predictions = []
    response_lengths = []
    
    for i, (sentence, reference) in enumerate(zip(test_sentences, test_references)):
        if i % 10 == 0:
            logger.info(f"  Processing {i+1}/{len(test_sentences)}...")
        
        try:
            # Build prompt
            prompt = build_prompt(tokenizer, sentence)
            
            # Generate response
            full_output = generate_response(model, tokenizer, prompt)
            
            # Extract clean response
            extracted_response = extract_response(full_output)
            
            # Store prediction
            predictions.append({
                "user_input": sentence,
                "reference": reference,
                "extracted_response": extracted_response
            })
            
            response_lengths.append(len(extracted_response.split()))
            
        except Exception as e:
            logger.error(f"  ❌ Error processing example {i+1}: {str(e)}")
            predictions.append({
                "user_input": sentence,
                "reference": reference,
                "extracted_response": f"Error: {str(e)}"
            })
            response_lengths.append(0)
    
    # Step 4: Save predictions
    logger.info("💾 Saving predictions to CSV...")
    predictions_df = pd.DataFrame(predictions)
    
    # Create output directory
    os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
    
    # Save to CSV
    predictions_df.to_csv(predictions_output_path, index=False)
    
    # Calculate statistics
    num_predictions = len(predictions)
    avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0.0
    
    logger.info(f"✅ Inference completed successfully!")
    logger.info(f"  📊 Generated {num_predictions} predictions")
    logger.info(f"  📏 Average response length: {avg_response_length:.1f} words")
    logger.info(f"  💾 Saved to: {predictions_output_path}")
    
    # Show sample predictions
    logger.info(f"📋 Sample predictions:")
    for i in range(min(3, len(predictions))):
        pred = predictions[i]
        logger.info(f"  {i+1}. Input: {pred['user_input'][:50]}...")
        logger.info(f"     Output: {pred['extracted_response'][:50]}...")
    
    return (num_predictions, avg_response_length)