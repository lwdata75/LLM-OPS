"""
Fine-tuning component for Phi-3 model with LoRA.
"""
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics
from typing import Dict


@component(
    base_image="pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel",
    packages_to_install=[
        "transformers==4.46.0",
        "peft==0.13.2",
        "datasets==3.0.0",
        "accelerate==1.0.1",
        "bitsandbytes==0.43.3",
        "trl==0.10.1",
        "tensorboard==2.17.0",
        "gcsfs==2024.9.0",
        "google-cloud-storage==2.18.2",
        "scipy",
    ],
)
def fine_tuning_component(
    train_dataset: Input[Dataset],
    model_name: str,
    lora_config: Dict,
    training_config: Dict,
    quantization_config: Dict,
    fine_tuned_model: Output[Model],
    training_metrics: Output[Metrics],
) -> Dict[str, float]:
    """Fine-tune Phi-3 model with LoRA on nutrition dataset.
    
    Args:
        train_dataset: Training dataset in JSON Lines format
        model_name: Hugging Face model identifier
        lora_config: LoRA configuration parameters
        training_config: Training hyperparameters
        quantization_config: Quantization configuration
        fine_tuned_model: Output path for the fine-tuned model
        training_metrics: Output path for training metrics
        
    Returns:
        Dictionary with final training metrics
    """
    import torch
    import json
    import logging
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    from datasets import load_dataset
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Loading model: {model_name}")
    logger.info(f"Using device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    
    # Configure quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=quantization_config["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(torch, quantization_config["bnb_4bit_compute_dtype"]),
        bnb_4bit_quant_type=quantization_config["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=quantization_config["bnb_4bit_use_double_quant"],
    )
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    # Prepare model for LoRA training
    model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA
    peft_config = LoraConfig(
        r=lora_config["r"],
        lora_alpha=lora_config["lora_alpha"],
        lora_dropout=lora_config["lora_dropout"],
        target_modules=lora_config["target_modules"],
        bias=lora_config["bias"],
        task_type=lora_config["task_type"],
    )
    
    model = get_peft_model(model, peft_config)
    
    # Log trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Trainable parameters: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
    
    # Load dataset
    logger.info(f"Loading training dataset from {train_dataset.path}")
    dataset = load_dataset("json", data_files=train_dataset.path, split="train")
    
    # Split for validation
    split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
    train_data = split_dataset["train"]
    eval_data = split_dataset["test"]
    
    logger.info(f"Training samples: {len(train_data)}")
    logger.info(f"Validation samples: {len(eval_data)}")
    
    # Configure training arguments
    training_args = TrainingArguments(
        output_dir="/tmp/training_output",
        num_train_epochs=training_config["num_train_epochs"],
        per_device_train_batch_size=training_config["per_device_train_batch_size"],
        per_device_eval_batch_size=training_config["per_device_eval_batch_size"],
        gradient_accumulation_steps=training_config["gradient_accumulation_steps"],
        learning_rate=training_config["learning_rate"],
        warmup_steps=training_config["warmup_steps"],
        logging_steps=training_config["logging_steps"],
        save_steps=training_config["save_steps"],
        eval_steps=training_config["eval_steps"],
        eval_strategy="steps",
        save_strategy="steps",
        fp16=True,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        logging_dir=training_metrics.path,
        report_to=["tensorboard"],
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )
    
    # Create trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=eval_data,
        tokenizer=tokenizer,
        max_seq_length=training_config["max_seq_length"],
        dataset_text_field="text",  # Use text field instead of messages
        packing=False,
    )
    
    # Train the model
    logger.info("Starting training...")
    train_result = trainer.train()
    
    # Save the fine-tuned model
    logger.info(f"Saving model to {fine_tuned_model.path}")
    trainer.model.save_pretrained(fine_tuned_model.path)
    tokenizer.save_pretrained(fine_tuned_model.path)
    
    # Log metrics
    final_metrics = {
        "train_loss": float(train_result.training_loss),
        "train_runtime": float(train_result.metrics.get("train_runtime", 0)),
        "train_samples_per_second": float(train_result.metrics.get("train_samples_per_second", 0)),
    }
    
    # Get final evaluation metrics
    eval_results = trainer.evaluate()
    final_metrics["eval_loss"] = float(eval_results.get("eval_loss", 0))
    
    logger.info(f"Training completed! Final metrics: {final_metrics}")
    
    # Log metrics to Kubeflow
    training_metrics.log_metric("train_loss", final_metrics["train_loss"])
    training_metrics.log_metric("eval_loss", final_metrics["eval_loss"])
    training_metrics.log_metric("trainable_params_pct", 100 * trainable_params / total_params)
    
    return final_metrics
