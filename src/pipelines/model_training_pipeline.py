"""
Main training pipeline definition for the nutrition assistant.
"""
from kfp import dsl
from typing import Dict

# Import components
from src.pipeline_components.data_transformation_component import data_transformation_component
from src.pipeline_components.fine_tuning_component import fine_tuning_component
from src.pipeline_components.inference_component import inference_component
from src.pipeline_components.evaluation_component import evaluation_component


@dsl.pipeline(
    name="nutrition-assistant-training-pipeline",
    description="End-to-end pipeline for fine-tuning Phi-3 on nutrition data",
)
def nutrition_training_pipeline(
    gcs_data_uri: str,
    model_name: str,
    train_test_split: float = 0.8,
    max_inference_samples: int = 100,
    lora_config: Dict = None,
    training_config: Dict = None,
    quantization_config: Dict = None,
):
    """Complete pipeline for training a nutrition assistant.
    
    Pipeline steps:
    1. Data transformation: Convert CSV to conversational format
    2. Fine-tuning: Train Phi-3 with LoRA
    3. Inference: Generate predictions on test set
    4. Evaluation: Compute RAGAS metrics
    
    Args:
        gcs_data_uri: GCS URI to the nutrition dataset CSV
        model_name: Hugging Face model identifier
        train_test_split: Ratio for train/test split
        max_inference_samples: Maximum samples for inference
        lora_config: LoRA configuration dictionary
        training_config: Training hyperparameters dictionary
        quantization_config: Quantization configuration dictionary
    """
    
    # Step 1: Transform data
    data_transform_task = data_transformation_component(
        gcs_data_uri=gcs_data_uri,
        train_test_split=train_test_split,
    )
    
    # Step 2: Fine-tune model
    fine_tuning_task = fine_tuning_component(
        train_dataset=data_transform_task.outputs["train_dataset"],
        model_name=model_name,
        lora_config=lora_config,
        training_config=training_config,
        quantization_config=quantization_config,
    )
    
    # Configure GPU resources for fine-tuning
    fine_tuning_task.set_accelerator_type("NVIDIA_TESLA_T4")
    fine_tuning_task.set_accelerator_limit(1)
    fine_tuning_task.set_cpu_limit("16")
    fine_tuning_task.set_memory_limit("50G")
    
    # Step 3: Generate predictions
    inference_task = inference_component(
        fine_tuned_model=fine_tuning_task.outputs["fine_tuned_model"],
        test_dataset=data_transform_task.outputs["test_dataset"],
        model_name=model_name,
        max_samples=max_inference_samples,
    )
    
    # Configure GPU resources for inference
    inference_task.set_accelerator_type("NVIDIA_TESLA_T4")
    inference_task.set_accelerator_limit(1)
    inference_task.set_cpu_limit("8")
    inference_task.set_memory_limit("32G")
    
    # Step 4: Evaluate predictions
    evaluation_task = evaluation_component(
        predictions=inference_task.outputs["predictions"],
    )
    
    # No GPU needed for evaluation
    evaluation_task.set_cpu_limit("4")
    evaluation_task.set_memory_limit("8G")
