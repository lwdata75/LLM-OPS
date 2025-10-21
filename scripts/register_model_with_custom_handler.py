"""
Script to register a fine-tuned model with a custom handler to Vertex AI Model Registry.

This script:
1. Uploads the handler.py file to the GCS model artifact directory
2. Registers the model to Vertex AI Model Registry using the pre-built HuggingFace container

Usage:
    python scripts/register_model_with_custom_handler.py \
        --model-uri gs://bucket/path/to/model \
        --model-name nutrition-assistant \
        --model-description "Fine-tuned Phi-3 for nutrition questions"
"""
import os
import argparse
from pathlib import Path
from google.cloud import storage, aiplatform
from dotenv import load_dotenv

load_dotenv()


def upload_handler_to_gcs(
    handler_file_path: str,
    model_artifact_uri: str,
    bucket_name: str = None
) -> str:
    """
    Upload the handler.py file to the GCS model artifact directory.
    
    Args:
        handler_file_path: Local path to the handler.py file
        model_artifact_uri: GCS URI of the model artifacts (gs://bucket/path/to/model)
        bucket_name: Optional bucket name override
        
    Returns:
        GCS URI where handler.py was uploaded
    """
    # Parse GCS URI
    if not model_artifact_uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI: {model_artifact_uri}")
    
    uri_parts = model_artifact_uri.replace("gs://", "").split("/", 1)
    if bucket_name is None:
        bucket_name = uri_parts[0]
    blob_prefix = uri_parts[1] if len(uri_parts) > 1 else ""
    
    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Upload handler.py
    handler_blob_name = f"{blob_prefix}/handler.py" if blob_prefix else "handler.py"
    blob = bucket.blob(handler_blob_name)
    
    print(f"📤 Uploading {handler_file_path} to gs://{bucket_name}/{handler_blob_name}")
    blob.upload_from_filename(handler_file_path)
    print(f"✅ Handler uploaded successfully!")
    
    return f"gs://{bucket_name}/{handler_blob_name}"


def register_model_to_vertex_ai(
    model_artifact_uri: str,
    model_name: str,
    model_description: str = None,
    parent_model: str = None,
    labels: dict = None,
    project_id: str = None,
    region: str = None
) -> aiplatform.Model:
    """
    Register the fine-tuned model to Vertex AI Model Registry.
    
    Args:
        model_artifact_uri: GCS URI of the model artifacts (must contain handler.py)
        model_name: Display name for the model
        model_description: Optional description
        parent_model: Optional parent model resource name for versioning
        labels: Optional labels dict
        project_id: GCP project ID
        region: GCP region
        
    Returns:
        The registered Model object
    """
    # Initialize Vertex AI
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    if region is None:
        region = os.getenv("GCP_REGION", "europe-west2")
    
    aiplatform.init(project=project_id, location=region)
    
    # Pre-built HuggingFace container for Vertex AI with PyTorch and Transformers
    # This container expects a handler.py file at the model artifact URI root
    serving_container_image_uri = (
        "us-docker.pkg.dev/deeplearning-platform-release/gcr.io/"
        "huggingface-pytorch-inference-cu121.2-3.transformers.4-46.ubuntu2204.py311"
    )
    
    print(f"\n{'='*80}")
    print(f"🚀 Registering model to Vertex AI Model Registry")
    print(f"{'='*80}")
    print(f"Model Name: {model_name}")
    print(f"Artifact URI: {model_artifact_uri}")
    print(f"Container: {serving_container_image_uri}")
    print(f"Project: {project_id}")
    print(f"Region: {region}")
    if parent_model:
        print(f"Parent Model (versioning): {parent_model}")
    print(f"{'='*80}\n")
    
    # Upload model
    model = aiplatform.Model.upload(
        display_name=model_name,
        description=model_description or f"Fine-tuned model: {model_name}",
        artifact_uri=model_artifact_uri,
        serving_container_image_uri=serving_container_image_uri,
        serving_container_ports=[8080],  # Required port for the pre-built container
        parent_model=parent_model,  # For versioning
        labels=labels or {},
    )
    
    print(f"\n✅ Model registered successfully!")
    print(f"Model Resource Name: {model.resource_name}")
    print(f"Model Version ID: {model.version_id}")
    print(f"🔗 View in console: https://console.cloud.google.com/vertex-ai/models/{model.name.split('/')[-1]}?project={project_id}")
    
    return model


def main():
    parser = argparse.ArgumentParser(
        description="Register a fine-tuned model with custom handler to Vertex AI"
    )
    parser.add_argument(
        "--model-uri",
        required=True,
        help="GCS URI of the model artifacts (gs://bucket/path/to/model)"
    )
    parser.add_argument(
        "--model-name",
        required=True,
        help="Display name for the model in Vertex AI"
    )
    parser.add_argument(
        "--model-description",
        default=None,
        help="Description for the model"
    )
    parser.add_argument(
        "--handler-path",
        default="src/handler.py",
        help="Local path to handler.py file (default: src/handler.py)"
    )
    parser.add_argument(
        "--parent-model",
        default=None,
        help="Parent model resource name for versioning (optional)"
    )
    parser.add_argument(
        "--project-id",
        default=None,
        help="GCP project ID (default: from .env)"
    )
    parser.add_argument(
        "--region",
        default=None,
        help="GCP region (default: from .env)"
    )
    
    args = parser.parse_args()
    
    # Validate handler file exists
    if not os.path.exists(args.handler_path):
        print(f"❌ Handler file not found: {args.handler_path}")
        return 1
    
    try:
        # Step 1: Upload handler to GCS
        print(f"\n{'='*80}")
        print("Step 1: Uploading handler.py to GCS")
        print(f"{'='*80}\n")
        
        handler_uri = upload_handler_to_gcs(
            handler_file_path=args.handler_path,
            model_artifact_uri=args.model_uri
        )
        
        # Step 2: Register model to Vertex AI
        print(f"\n{'='*80}")
        print("Step 2: Registering model to Vertex AI Model Registry")
        print(f"{'='*80}\n")
        
        model = register_model_to_vertex_ai(
            model_artifact_uri=args.model_uri,
            model_name=args.model_name,
            model_description=args.model_description,
            parent_model=args.parent_model,
            project_id=args.project_id,
            region=args.region
        )
        
        print(f"\n{'='*80}")
        print("✅ Model registration completed successfully!")
        print(f"{'='*80}\n")
        print("Next steps:")
        print("1. Go to Vertex AI Model Registry in GCP Console")
        print("2. Find your model and click 'Deploy to Endpoint'")
        print("3. Configure the endpoint with GPU (T4) and appropriate machine type")
        print("4. Wait for deployment to complete (15-30 minutes)")
        print(f"\n{'='*80}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
