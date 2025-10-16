"""
Kubeflow Pipeline for Yoda sentence model training data preparation.
"""

import os
import sys
from kfp.dsl import pipeline

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.pipeline_components.data_transformation_component import data_transformation_component

@pipeline(
    name="yoda-data-preprocessing-pipeline",
    description="Pipeline to preprocess Yoda sentences dataset for Phi-3 fine-tuning",
    pipeline_root="gs://llmops_101_europ/pipeline_runs"
)
def yoda_data_preprocessing_pipeline(
    input_gcs_path: str = "gs://llmops_101_europ/15-10-2025-08:50:00/yoda_sentences.csv",
    output_gcs_bucket: str = "llmops_101_europ",
    test_size: float = 0.2,
    random_state: int = 42,
    use_extra_translation: bool = True
):
    """
    Yoda data preprocessing pipeline.
    
    Args:
        input_gcs_path (str): GCS path to input CSV file
        output_gcs_bucket (str): GCS bucket name for output files
        test_size (float): Proportion of test set (default: 0.2)
        random_state (int): Random seed for reproducibility (default: 42)
        use_extra_translation (bool): Whether to use translation_extra column (default: True)
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
    
    # Set resource limits (optional)
    data_transform_task.set_cpu_request("1")
    data_transform_task.set_memory_request("2Gi")
    data_transform_task.set_cpu_limit("2")
    data_transform_task.set_memory_limit("4Gi")

if __name__ == "__main__":
    # This allows testing the pipeline definition
    print("✅ Pipeline definition created successfully!")
    print("Pipeline name: yoda-data-preprocessing-pipeline")
    print("Components: data_transformation_component")
    print("Default parameters:")
    print(f"  - input_gcs_path: gs://llmops_101_europ/15-10-2025-08:50:00/yoda_sentences.csv")
    print(f"  - output_gcs_bucket: llmops_101_europ")
    print(f"  - test_size: 0.2")
    print(f"  - random_state: 42")
    print(f"  - use_extra_translation: True")