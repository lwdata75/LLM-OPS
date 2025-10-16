"""
Kubeflow Pipeline for Yoda sentence model training with Phi-3 fine-tuning.
"""

import os
import sys
from kfp.dsl import pipeline

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.pipeline_components.data_transformation_component import data_transformation_component
from src.pipeline_components.fine_tuning_component import fine_tuning_component

@pipeline(
    name="yoda-model-training-pipeline",
    description="Pipeline to preprocess Yoda sentences dataset and fine-tune Phi-3 with LoRA",
    pipeline_root="gs://llmops_101_europ/pipeline_runs"
)
def yoda_model_training_pipeline(
    input_gcs_path: str = "gs://llmops_101_europ/15-10-2025-08:50:00/yoda_sentences.csv",
    output_gcs_bucket: str = "llmops_101_europ",
    test_size: float = 0.2,
    random_state: int = 42,
    use_extra_translation: bool = True,
    # Fine-tuning hyperparameters
    model_name: str = "microsoft/Phi-3-mini-4k-instruct",
    learning_rate: float = 2e-4,
    num_train_epochs: int = 1,
    per_device_train_batch_size: int = 1,
    gradient_accumulation_steps: int = 4,
    lora_r: int = 16,
    lora_alpha: int = 32
):
    """
    Yoda model training pipeline with data preprocessing and Phi-3 fine-tuning.
    
    Args:
        input_gcs_path (str): GCS path to input CSV file
        output_gcs_bucket (str): GCS bucket name for output files
        test_size (float): Proportion of test set (default: 0.2)
        random_state (int): Random seed for reproducibility (default: 42)
        use_extra_translation (bool): Whether to use translation_extra column (default: True)
        model_name (str): Hugging Face model name for fine-tuning
        learning_rate (float): Learning rate for fine-tuning
        num_train_epochs (int): Number of training epochs
        per_device_train_batch_size (int): Batch size per device
        gradient_accumulation_steps (int): Gradient accumulation steps
        lora_r (int): LoRA rank parameter
        lora_alpha (int): LoRA alpha parameter
    """
    
    # Data transformation step
    data_transform_task = data_transformation_component(
        input_gcs_path=input_gcs_path,
        output_gcs_bucket=output_gcs_bucket,
        test_size=test_size,
        random_state=random_state,
        use_extra_translation=use_extra_translation
    )
    
    # Set display name for better visualization in Vertex AI
    data_transform_task.set_display_name("Data Transformation")
    
    # Set resource limits for data transformation
    data_transform_task.set_cpu_request("1")
    data_transform_task.set_memory_request("2Gi")
    data_transform_task.set_cpu_limit("2")
    data_transform_task.set_memory_limit("4Gi")
    
    # Fine-tuning step
    fine_tuning_task = fine_tuning_component(
        train_dataset=data_transform_task.outputs["train_output_path"],
        model_name=model_name,
        learning_rate=learning_rate,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        lora_r=lora_r,
        lora_alpha=lora_alpha
    )
    
    # Set display name for better visualization in Vertex AI
    fine_tuning_task.set_display_name("Phi-3 Fine-tuning with LoRA")
    
    # Set GPU and resource requirements for fine-tuning
    fine_tuning_task.set_accelerator_type("NVIDIA_TESLA_T4")
    fine_tuning_task.set_cpu_limit("16")
    fine_tuning_task.set_memory_limit("50G")
    fine_tuning_task.set_cpu_request("8")
    fine_tuning_task.set_memory_request("25G")

if __name__ == "__main__":
    # This allows testing the pipeline definition
    print("✅ Pipeline definition created successfully!")
    print("Pipeline name: yoda-model-training-pipeline")
    print("Components: data_transformation_component, fine_tuning_component")
    print("Default parameters:")
    print(f"  - input_gcs_path: gs://llmops_101_europ/15-10-2025-08:50:00/yoda_sentences.csv")
    print(f"  - output_gcs_bucket: llmops_101_europ")
    print(f"  - test_size: 0.2")
    print(f"  - random_state: 42")
    print(f"  - use_extra_translation: True")
    print(f"  - model_name: microsoft/Phi-3-mini-4k-instruct")
    print(f"  - learning_rate: 2e-4")
    print(f"  - num_train_epochs: 1")
    print(f"  - per_device_train_batch_size: 1")
    print(f"  - gradient_accumulation_steps: 4")
    print(f"  - lora_r: 16")
    print(f"  - lora_alpha: 32")