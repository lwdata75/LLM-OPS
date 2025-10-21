"""
Constants and configuration for the LLM OPS pipeline.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GCP Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
GCP_REGION = os.getenv("GCP_REGION", "europe-west2")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "llmops_101_europ")

# GCS Paths
GCS_BUCKET_URI = f"gs://{GCP_BUCKET_NAME}"
GCS_PIPELINE_ROOT = f"{GCS_BUCKET_URI}/pipeline_root"
GCS_DATA_PATH = f"{GCS_BUCKET_URI}/data"
GCS_MODEL_PATH = f"{GCS_BUCKET_URI}/models"

# Model Configuration
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
PIPELINE_NAME = "nutrition-assistant-training-pipeline"

# Training Hyperparameters
TRAINING_CONFIG = {
    "max_seq_length": 512,
    "num_train_epochs": 3,
    "per_device_train_batch_size": 2,
    "per_device_eval_batch_size": 2,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-4,
    "warmup_steps": 100,
    "logging_steps": 10,
    "save_steps": 100,
    "eval_steps": 50,
}

# LoRA Configuration
LORA_CONFIG = {
    "r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "bias": "none",
    "task_type": "CAUSAL_LM",
}

# Quantization Configuration
QUANTIZATION_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_compute_dtype": "float16",
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_use_double_quant": True,
}

# Data Configuration
TRAIN_TEST_SPLIT = 0.8
EVAL_SPLIT = 0.1  # From training data
MAX_INFERENCE_SAMPLES = 100  # For evaluation

# Docker Images
BASE_PYTHON_IMAGE = "python:3.11-slim"
PYTORCH_GPU_IMAGE = "pytorch/pytorch:2.5.0-cuda12.4-cudnn9-devel"
GIT_PYTHON_IMAGE = "cicirello/pyaction:3.11"
