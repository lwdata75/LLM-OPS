"""
Pipeline runner script for Vertex AI Pipelines.
Compiles and submits the Yoda data preprocessing pipeline.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import aiplatform
from kfp.compiler import Compiler

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.pipelines.model_training_pipeline import yoda_model_training_pipeline

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "europe-west2")
BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
PIPELINE_ROOT = f"gs://{BUCKET_NAME}/pipeline_runs"

# Pipeline configuration
PIPELINE_NAME = "yoda-model-training"
DISPLAY_NAME = "Yoda Model Training Pipeline with Fine-tuning"

def compile_pipeline():
    """Compile the pipeline to a JSON file."""
    print("🔧 Compiling pipeline...")
    
    # Create output directory if it doesn't exist
    os.makedirs("pipeline_artifacts", exist_ok=True)
    
    # Define the compiled pipeline path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    compiled_pipeline_path = f"pipeline_artifacts/{PIPELINE_NAME}_{timestamp}.json"
    
    # Compile the pipeline
    compiler = Compiler()
    compiler.compile(
        pipeline_func=yoda_model_training_pipeline,
        package_path=compiled_pipeline_path
    )
    
    print(f"✅ Pipeline compiled successfully to: {compiled_pipeline_path}")
    return compiled_pipeline_path

def submit_pipeline(compiled_pipeline_path: str):
    """Submit the pipeline to Vertex AI."""
    print("🚀 Submitting pipeline to Vertex AI...")
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Create a unique job name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_name = f"{PIPELINE_NAME}-{timestamp}"
    
    # Define pipeline parameters
    pipeline_parameters = {
        "input_gcs_path": f"gs://{BUCKET_NAME}/15-10-2025-08:50:00/yoda_sentences.csv",
        "output_gcs_bucket": BUCKET_NAME,
        "test_size": 0.2,
        "random_state": 42,
        "use_extra_translation": True,
        # Fine-tuning parameters
        "model_name": "microsoft/Phi-3-mini-4k-instruct",
        "learning_rate": 2e-4,
        "num_train_epochs": 1,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "lora_r": 16,
        "lora_alpha": 32
    }
    
    # Submit the pipeline job
    job = aiplatform.PipelineJob(
        display_name=f"{DISPLAY_NAME} - {timestamp}",
        template_path=compiled_pipeline_path,
        pipeline_root=PIPELINE_ROOT,
        parameter_values=pipeline_parameters,
        enable_caching=True
    )
    
    print(f"📊 Pipeline job details:")
    print(f"   Job name: {job_name}")
    print(f"   Display name: {DISPLAY_NAME} - {timestamp}")
    print(f"   Pipeline root: {PIPELINE_ROOT}")
    print(f"   Parameters: {pipeline_parameters}")
    
    # Submit the job
    job.submit(service_account=None)
    
    print(f"✅ Pipeline submitted successfully!")
    print(f"🔗 View the pipeline run at:")
    print(f"   https://console.cloud.google.com/vertex-ai/pipelines/runs?project={PROJECT_ID}")
    print(f"🆔 Job resource name: {job.resource_name}")
    
    return job

def main():
    """Main function to compile and submit the pipeline."""
    print("=" * 60)
    print("🤖 Yoda Model Training Pipeline Runner")
    print("=" * 60)
    
    # Validate environment variables
    if not all([PROJECT_ID, REGION, BUCKET_NAME]):
        print("❌ Error: Missing required environment variables!")
        print(f"   GCP_PROJECT_ID: {PROJECT_ID or 'NOT SET'}")
        print(f"   GCP_REGION: {REGION or 'NOT SET'}")
        print(f"   GCP_BUCKET_NAME: {BUCKET_NAME or 'NOT SET'}")
        print("\nPlease check your .env file.")
        return False
    
    print(f"📋 Configuration:")
    print(f"   Project ID: {PROJECT_ID}")
    print(f"   Region: {REGION}")
    print(f"   Bucket: {BUCKET_NAME}")
    print(f"   Pipeline root: {PIPELINE_ROOT}")
    print()
    
    try:
        # Step 1: Compile the pipeline
        compiled_pipeline_path = compile_pipeline()
        
        # Step 2: Submit the pipeline
        job = submit_pipeline(compiled_pipeline_path)
        
        print("\n" + "=" * 60)
        print("🎉 Pipeline execution started successfully!")
        print("=" * 60)
        print(f"📁 Compiled pipeline saved to: {compiled_pipeline_path}")
        print(f"🔍 Monitor the pipeline execution in the GCP console.")
        print(f"📊 Check for output datasets in: gs://{BUCKET_NAME}/processed_data/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please check your GCP authentication and permissions.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)