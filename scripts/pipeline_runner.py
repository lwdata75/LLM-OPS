"""
Pipeline runner script to compile and submit the pipeline to Vertex AI.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import aiplatform
from kfp import compiler
import logging
from datetime import datetime

from src.constants import (
    GCP_PROJECT_ID,
    GCP_REGION,
    GCS_PIPELINE_ROOT,
    GCS_BUCKET_URI,
    MODEL_NAME,
    PIPELINE_NAME,
    TRAINING_CONFIG,
    LORA_CONFIG,
    QUANTIZATION_CONFIG,
    TRAIN_TEST_SPLIT,
    MAX_INFERENCE_SAMPLES,
)
from src.pipelines.model_training_pipeline import nutrition_training_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compile_pipeline(output_file: str = "compiled_pipeline.yaml"):
    """Compile the Kubeflow pipeline to YAML.
    
    Args:
        output_file: Output filename for compiled pipeline
    """
    logger.info(f"Compiling pipeline to {output_file}")
    
    compiler.Compiler().compile(
        pipeline_func=nutrition_training_pipeline,
        package_path=output_file,
    )
    
    logger.info(f"✅ Pipeline compiled successfully to {output_file}")
    return output_file


def submit_pipeline(
    compiled_pipeline_path: str,
    enable_caching: bool = False,
):
    """Submit the compiled pipeline to Vertex AI.
    
    Args:
        compiled_pipeline_path: Path to compiled pipeline YAML
        enable_caching: Whether to enable pipeline caching
    """
    # Initialize Vertex AI
    logger.info(f"Initializing Vertex AI with project: {GCP_PROJECT_ID}, region: {GCP_REGION}")
    aiplatform.init(
        project=GCP_PROJECT_ID,
        location=GCP_REGION,
    )
    
    # Prepare pipeline parameters
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gcs_data_uri = f"{GCS_BUCKET_URI}/COMBINED_FOOD_DATASET.csv"
    
    pipeline_params = {
        "gcs_data_uri": gcs_data_uri,
        "model_name": MODEL_NAME,
        "train_test_split": TRAIN_TEST_SPLIT,
        "max_inference_samples": MAX_INFERENCE_SAMPLES,
        "lora_config": LORA_CONFIG,
        "training_config": TRAINING_CONFIG,
        "quantization_config": QUANTIZATION_CONFIG,
    }
    
    logger.info(f"Pipeline parameters:")
    logger.info(f"  - Data URI: {gcs_data_uri}")
    logger.info(f"  - Model: {MODEL_NAME}")
    logger.info(f"  - Train/Test Split: {TRAIN_TEST_SPLIT}")
    logger.info(f"  - Max Inference Samples: {MAX_INFERENCE_SAMPLES}")
    
    # Create pipeline job
    job_name = f"{PIPELINE_NAME}_{timestamp}"
    
    logger.info(f"\n🚀 Submitting pipeline job: {job_name}")
    
    job = aiplatform.PipelineJob(
        display_name=job_name,
        template_path=compiled_pipeline_path,
        pipeline_root=GCS_PIPELINE_ROOT,
        parameter_values=pipeline_params,
        enable_caching=enable_caching,
    )
    
    # Submit the job
    job.submit()
    
    logger.info(f"\n✅ Pipeline job submitted successfully!")
    logger.info(f"📊 Job name: {job_name}")
    logger.info(f"🔗 View pipeline execution in GCP Console:")
    logger.info(f"   https://console.cloud.google.com/vertex-ai/pipelines/runs/{job.resource_name.split('/')[-1]}?project={GCP_PROJECT_ID}")
    logger.info(f"\n⏳ Pipeline is now running on Vertex AI...")
    logger.info(f"   You can monitor progress in the GCP Console link above")
    
    return job


def run_pipeline(compile_only: bool = False, enable_caching: bool = False):
    """Main function to compile and optionally submit the pipeline.
    
    Args:
        compile_only: If True, only compile without submitting
        enable_caching: Whether to enable pipeline caching
    """
    try:
        # Compile the pipeline
        compiled_pipeline = compile_pipeline("compiled_nutrition_pipeline.yaml")
        
        if compile_only:
            logger.info("✅ Compilation complete. Skipping submission (compile_only=True)")
            return None
        
        # Submit to Vertex AI
        job = submit_pipeline(compiled_pipeline, enable_caching=enable_caching)
        
        return job
        
    except Exception as e:
        logger.error(f"❌ Error running pipeline: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the nutrition training pipeline")
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Only compile the pipeline without submitting to Vertex AI"
    )
    parser.add_argument(
        "--enable-caching",
        action="store_true",
        help="Enable pipeline caching"
    )
    
    args = parser.parse_args()
    
    run_pipeline(
        compile_only=args.compile_only,
        enable_caching=args.enable_caching,
    )
