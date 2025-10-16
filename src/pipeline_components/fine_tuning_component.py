"""
Kubeflow Pipeline component for fine-tuning Phi-3 with LoRA.
Takes training dataset and outputs fine-tuned model and training metrics.
"""

from kfp.dsl import component, InputPath, OutputPath
from typing import NamedTuple

@component(
    base_image="pytorch/pytorch:2.8.0-cuda12.9-cudnn9-devel",
    packages_to_install=[
        "transformers==4.46.3",
        "peft==0.13.2",
        "trl",
        "datasets==4.2.0",
        "pandas==2.3.3",
        "accelerate",
        "bitsandbytes",
        "tensorboard",
        "google-cloud-storage==2.19.0",
        "gcsfs==2025.9.0"
    ]
)
def fine_tuning_component(
    train_dataset: InputPath(str),
    model_output_path: OutputPath(str),
    metrics_output_path: OutputPath(str),
    model_name: str = "microsoft/Phi-3-mini-4k-instruct",
    max_seq_length: int = 512,
    learning_rate: float = 2e-4,
    num_train_epochs: int = 1,
    per_device_train_batch_size: int = 1,
    per_device_eval_batch_size: int = 1,
    gradient_accumulation_steps: int = 4,
    warmup_steps: int = 100,
    logging_steps: int = 10,
    eval_steps: int = 50,
    save_steps: int = 100,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.1,
    eval_split_ratio: float = 0.2
) -> NamedTuple("FineTuningOutput", [
    ("total_params", int), 
    ("trainable_params", int), 
    ("final_train_loss", float),
    ("final_eval_loss", float)
]):
    """
    Fine-tune Phi-3 model using LoRA (Low-Rank Adaptation).
    
    Args:
        train_dataset (InputPath): Path to training dataset in JSON format
        model_output_path (OutputPath): Path to save fine-tuned model
        metrics_output_path (OutputPath): Path to save training metrics and TensorBoard logs
        model_name (str): Hugging Face model name/path
        max_seq_length (int): Maximum sequence length for training
        learning_rate (float): Learning rate for training
        num_train_epochs (int): Number of training epochs
        per_device_train_batch_size (int): Batch size per device for training
        per_device_eval_batch_size (int): Batch size per device for evaluation
        gradient_accumulation_steps (int): Gradient accumulation steps
        warmup_steps (int): Warmup steps for learning rate scheduler
        logging_steps (int): Steps between logging
        eval_steps (int): Steps between evaluations
        save_steps (int): Steps between model saves
        lora_r (int): LoRA rank parameter
        lora_alpha (int): LoRA alpha parameter
        lora_dropout (float): LoRA dropout rate
        eval_split_ratio (float): Ratio to split train data for evaluation
        
    Returns:
        NamedTuple: Training statistics (total_params, trainable_params, final_train_loss, final_eval_loss)
    """
    import os
    import json
    import logging
    import torch
    import pandas as pd
    from datasets import Dataset
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        BitsAndBytesConfig
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer, SFTConfig
    from google.cloud import storage
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Phi-3 fine-tuning with LoRA")
    logger.info(f"💾 CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"🎯 Device: {torch.cuda.get_device_name()}")
        logger.info(f"💾 CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Define hyperparameters
    hyperparameters = {
        "model_name": model_name,
        "max_seq_length": max_seq_length,
        "learning_rate": learning_rate,
        "num_train_epochs": num_train_epochs,
        "per_device_train_batch_size": per_device_train_batch_size,
        "per_device_eval_batch_size": per_device_eval_batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "warmup_steps": warmup_steps,
        "logging_steps": logging_steps,
        "eval_steps": eval_steps,
        "save_steps": save_steps,
        "lora_r": lora_r,
        "lora_alpha": lora_alpha,
        "lora_dropout": lora_dropout,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    }
    
    logger.info("📋 Hyperparameters:")
    for key, value in hyperparameters.items():
        logger.info(f"  {key}: {value}")
    
    # LoRA Configuration
    lora_config = LoraConfig(
        r=hyperparameters["lora_r"],
        lora_alpha=hyperparameters["lora_alpha"], 
        target_modules=hyperparameters["target_modules"],
        lora_dropout=hyperparameters["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    logger.info(f"✅ LoRA Config created:")
    logger.info(f"  Rank (r): {lora_config.r}")
    logger.info(f"  Alpha: {lora_config.lora_alpha}")
    logger.info(f"  Target modules: {lora_config.target_modules}")
    
    # BitsAndBytes Configuration for 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    logger.info("✅ BitsAndBytes Config created (4-bit quantization enabled)")
    
    # Load tokenizer
    logger.info(f"🔄 Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    
    # Ensure the tokenizer has a pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        logger.info("  ➕ Added pad token")
    
    logger.info(f"✅ Tokenizer loaded:")
    logger.info(f"  Vocab size: {tokenizer.vocab_size}")
    logger.info(f"  Pad token: {tokenizer.pad_token}")
    
    # Load model with quantization
    logger.info(f"🔄 Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    logger.info(f"✅ Model loaded:")
    logger.info(f"  Model type: {type(model).__name__}")
    logger.info(f"  Device: {next(model.parameters()).device}")
    logger.info(f"  Data type: {next(model.parameters()).dtype}")
    
    # Count parameters before LoRA
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params_before = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    logger.info(f"📊 Parameters before LoRA:")
    logger.info(f"  Total parameters: {total_params:,}")
    logger.info(f"  Trainable parameters: {trainable_params_before:,}")
    
    # Prepare model for training and apply LoRA
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)
    
    # Count parameters after LoRA
    total_params_lora = sum(p.numel() for p in model.parameters())
    trainable_params_lora = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    logger.info(f"📊 Parameters after LoRA:")
    logger.info(f"  Total parameters: {total_params_lora:,}")
    logger.info(f"  Trainable parameters: {trainable_params_lora:,}")
    logger.info(f"  Trainable %: {100 * trainable_params_lora / total_params_lora:.2f}%")
    logger.info(f"  🎯 Parameter reduction: {100 * (1 - trainable_params_lora / total_params):.2f}%")
    
    # Print LoRA adapters info
    model.print_trainable_parameters()
    
    # Load training dataset
    logger.info(f"📂 Loading training dataset from: {train_dataset}")
    with open(train_dataset, 'r') as f:
        raw_data = [json.loads(line) for line in f]
    
    # Convert to Dataset
    df = pd.DataFrame(raw_data)
    dataset = Dataset.from_pandas(df)
    
    logger.info(f"✅ Dataset loaded successfully:")
    logger.info(f"  Number of examples: {len(dataset)}")
    logger.info(f"  Features: {dataset.features}")
    
    # Split the dataset for training and validation
    logger.info(f"🔀 Splitting dataset (eval_split_ratio={eval_split_ratio})")
    split_dataset = dataset.train_test_split(test_size=eval_split_ratio, seed=42)
    train_ds = split_dataset["train"]
    eval_ds = split_dataset["test"]
    
    logger.info(f"✅ Dataset split completed:")
    logger.info(f"  Training examples: {len(train_ds)}")
    logger.info(f"  Validation examples: {len(eval_ds)}")
    
    # Create output directories
    os.makedirs(model_output_path, exist_ok=True)
    os.makedirs(metrics_output_path, exist_ok=True)
    
    # Training Configuration with TensorBoard logging
    training_args = SFTConfig(
        output_dir=model_output_path,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        per_device_eval_batch_size=per_device_eval_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        warmup_steps=warmup_steps,
        logging_steps=logging_steps,
        eval_steps=eval_steps,
        save_steps=save_steps,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to=["tensorboard"],  # Enable TensorBoard logging
        logging_dir=metrics_output_path,  # TensorBoard logs to metrics output
        max_seq_length=max_seq_length,
        remove_unused_columns=False,
        dataloader_drop_last=True,
    )
    
    logger.info(f"✅ Training Config created:")
    logger.info(f"  Output dir: {training_args.output_dir}")
    logger.info(f"  Logging dir: {training_args.logging_dir}")
    logger.info(f"  Max sequence length: {training_args.max_seq_length}")
    
    # Initialize SFT Trainer
    logger.info("🏋️ Initializing SFT Trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
        peft_config=lora_config,
    )
    
    logger.info(f"✅ SFT Trainer initialized")
    logger.info(f"  Training examples: {len(trainer.train_dataset)}")
    logger.info(f"  Evaluation examples: {len(trainer.eval_dataset)}")
    
    # Start training
    logger.info("🚀 Starting fine-tuning process...")
    try:
        trainer.train()
        logger.info("✅ Training completed successfully!")
        
        # Save the final model
        trainer.save_model()
        logger.info(f"💾 Model saved to: {model_output_path}")
        
        # Save hyperparameters and training info
        training_info = {
            "hyperparameters": hyperparameters,
            "total_params": total_params_lora,
            "trainable_params": trainable_params_lora,
            "training_examples": len(train_ds),
            "validation_examples": len(eval_ds),
            "model_name": model_name,
            "lora_config": {
                "r": lora_config.r,
                "alpha": lora_config.lora_alpha,
                "target_modules": lora_config.target_modules,
                "dropout": lora_config.lora_dropout
            }
        }
        
        # Save training info to metrics path
        with open(os.path.join(metrics_output_path, "training_info.json"), 'w') as f:
            json.dump(training_info, f, indent=2)
        
        # Extract final metrics
        final_train_loss = 0.0
        final_eval_loss = 0.0
        
        # Get final losses from training history
        if trainer.state.log_history:
            # Find the last train and eval losses
            for log in reversed(trainer.state.log_history):
                if 'train_loss' in log and final_train_loss == 0.0:
                    final_train_loss = log['train_loss']
                if 'eval_loss' in log and final_eval_loss == 0.0:
                    final_eval_loss = log['eval_loss']
                if final_train_loss > 0.0 and final_eval_loss > 0.0:
                    break
        
        logger.info(f"📊 Final training metrics:")
        logger.info(f"  Final train loss: {final_train_loss:.4f}")
        logger.info(f"  Final eval loss: {final_eval_loss:.4f}")
        
        # Log metrics to Kubeflow
        from kfp.v2.dsl import Metrics
        
        # Create metrics artifact
        metrics = Metrics()
        metrics.log_metric("total_parameters", total_params_lora)
        metrics.log_metric("trainable_parameters", trainable_params_lora)
        metrics.log_metric("trainable_percentage", 100 * trainable_params_lora / total_params_lora)
        metrics.log_metric("final_train_loss", final_train_loss)
        metrics.log_metric("final_eval_loss", final_eval_loss)
        metrics.log_metric("training_examples", len(train_ds))
        metrics.log_metric("validation_examples", len(eval_ds))
        metrics.log_metric("lora_rank", lora_config.r)
        metrics.log_metric("lora_alpha", lora_config.lora_alpha)
        
        # Log hyperparameters
        for key, value in hyperparameters.items():
            if isinstance(value, (int, float)):
                metrics.log_metric(f"hp_{key}", value)
        
        # Save metrics artifact
        with open(os.path.join(metrics_output_path, "metrics.json"), 'w') as f:
            json.dump({
                "total_parameters": total_params_lora,
                "trainable_parameters": trainable_params_lora,
                "trainable_percentage": 100 * trainable_params_lora / total_params_lora,
                "final_train_loss": final_train_loss,
                "final_eval_loss": final_eval_loss,
                "training_examples": len(train_ds),
                "validation_examples": len(eval_ds),
                "lora_rank": lora_config.r,
                "lora_alpha": lora_config.lora_alpha
            }, f, indent=2)
        
        logger.info("✅ Fine-tuning component completed successfully!")
        
        return (total_params_lora, trainable_params_lora, final_train_loss, final_eval_loss)
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}")
        raise e