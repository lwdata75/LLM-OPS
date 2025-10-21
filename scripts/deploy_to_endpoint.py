"""
Script to deploy the registered model to a Vertex AI endpoint.

This script:
1. Creates a new Vertex AI endpoint (if needed)
2. Deploys the registered model to the endpoint with GPU configuration
3. Waits for deployment to complete

Usage:
    python scripts/deploy_to_endpoint.py --model-id 3561348948692041728
"""
import os
import argparse
import time
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()


def create_endpoint(
    endpoint_name: str,
    project_id: str = None,
    region: str = None
) -> aiplatform.Endpoint:
    """
    Create a new Vertex AI endpoint.
    
    Args:
        endpoint_name: Display name for the endpoint
        project_id: GCP project ID
        region: GCP region
        
    Returns:
        Created Endpoint object
    """
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    if region is None:
        region = os.getenv("GCP_REGION", "europe-west2")
    
    aiplatform.init(project=project_id, location=region)
    
    print(f"\n{'='*80}")
    print("📍 Creating Vertex AI Endpoint")
    print(f"{'='*80}")
    print(f"Endpoint Name: {endpoint_name}")
    print(f"Project: {project_id}")
    print(f"Region: {region}")
    print(f"{'='*80}\n")
    
    endpoint = aiplatform.Endpoint.create(
        display_name=endpoint_name,
        project=project_id,
        location=region,
    )
    
    print(f"✅ Endpoint created: {endpoint.resource_name}")
    print(f"Endpoint ID: {endpoint.name.split('/')[-1]}")
    
    return endpoint


def deploy_model_to_endpoint(
    model_id: str,
    endpoint_name: str = "nutrition-assistant-endpoint",
    machine_type: str = "n1-standard-8",
    accelerator_type: str = "NVIDIA_TESLA_T4",
    accelerator_count: int = 1,
    min_replica_count: int = 1,
    max_replica_count: int = 1,
    project_id: str = None,
    region: str = None
) -> tuple:
    """
    Deploy a model to a Vertex AI endpoint.
    
    Args:
        model_id: Model ID or full resource name
        endpoint_name: Name for the endpoint
        machine_type: Machine type (e.g., n1-standard-8)
        accelerator_type: GPU type (e.g., NVIDIA_TESLA_T4)
        accelerator_count: Number of GPUs
        min_replica_count: Minimum number of replicas
        max_replica_count: Maximum number of replicas
        project_id: GCP project ID
        region: GCP region
        
    Returns:
        Tuple of (endpoint, deployed_model_id)
    """
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    if region is None:
        region = os.getenv("GCP_REGION", "europe-west2")
    
    aiplatform.init(project=project_id, location=region)
    
    print(f"\n{'='*80}")
    print("🚀 Starting Model Deployment")
    print(f"{'='*80}")
    
    # Get the model
    print(f"📦 Loading model: {model_id}")
    if "/" in model_id:
        model = aiplatform.Model(model_name=model_id)
    else:
        model = aiplatform.Model(model_name=f"projects/{project_id}/locations/{region}/models/{model_id}")
    
    print(f"✅ Model loaded: {model.display_name}")
    print(f"   Resource: {model.resource_name}")
    
    # Check if endpoint exists
    print(f"\n🔍 Checking for existing endpoint: {endpoint_name}")
    existing_endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{endpoint_name}"',
        order_by="create_time desc"
    )
    
    if existing_endpoints:
        endpoint = existing_endpoints[0]
        print(f"✅ Using existing endpoint: {endpoint.display_name}")
        print(f"   Endpoint ID: {endpoint.name.split('/')[-1]}")
    else:
        print(f"📍 Creating new endpoint...")
        endpoint = create_endpoint(endpoint_name, project_id, region)
    
    # Deploy model to endpoint
    print(f"\n{'='*80}")
    print("🚀 Deploying Model to Endpoint")
    print(f"{'='*80}")
    print(f"Configuration:")
    print(f"  Machine Type: {machine_type}")
    print(f"  Accelerator: {accelerator_type} x {accelerator_count}")
    print(f"  Replicas: {min_replica_count} (min) - {max_replica_count} (max)")
    print(f"{'='*80}\n")
    
    print("⏳ Deploying... This will take 15-30 minutes.")
    print("   You can close this window - deployment will continue in the background.")
    print(f"   Monitor at: https://console.cloud.google.com/vertex-ai/endpoints/{endpoint.name.split('/')[-1]}?project={project_id}")
    
    start_time = time.time()
    
    # Deploy the model
    deployed_model = model.deploy(
        endpoint=endpoint,
        deployed_model_display_name=f"{model.display_name}-deployment",
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
        traffic_percentage=100,
        sync=True,  # Wait for deployment to complete
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("✅ Deployment Complete!")
    print(f"{'='*80}")
    print(f"⏱️  Time taken: {elapsed_time/60:.1f} minutes")
    print(f"🎯 Endpoint: {endpoint.display_name}")
    print(f"📍 Endpoint ID: {endpoint.name.split('/')[-1]}")
    print(f"🔗 Console: https://console.cloud.google.com/vertex-ai/endpoints/{endpoint.name.split('/')[-1]}?project={project_id}")
    print(f"{'='*80}\n")
    
    # Save endpoint ID to .env instructions
    endpoint_id = endpoint.name.split('/')[-1]
    print("📝 Add this to your .env file:")
    print(f"   GCP_ENDPOINT_ID={endpoint_id}")
    print()
    
    return endpoint, endpoint_id


def main():
    parser = argparse.ArgumentParser(
        description="Deploy model to Vertex AI endpoint"
    )
    parser.add_argument(
        "--model-id",
        required=True,
        help="Model ID or full resource name"
    )
    parser.add_argument(
        "--endpoint-name",
        default="nutrition-assistant-endpoint",
        help="Display name for the endpoint"
    )
    parser.add_argument(
        "--machine-type",
        default="n1-standard-8",
        help="Machine type (default: n1-standard-8)"
    )
    parser.add_argument(
        "--accelerator-type",
        default="NVIDIA_TESLA_T4",
        help="GPU accelerator type (default: NVIDIA_TESLA_T4)"
    )
    parser.add_argument(
        "--accelerator-count",
        type=int,
        default=1,
        help="Number of accelerators (default: 1)"
    )
    parser.add_argument(
        "--min-replicas",
        type=int,
        default=1,
        help="Minimum replica count (default: 1)"
    )
    parser.add_argument(
        "--max-replicas",
        type=int,
        default=1,
        help="Maximum replica count (default: 1)"
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
    
    try:
        endpoint, endpoint_id = deploy_model_to_endpoint(
            model_id=args.model_id,
            endpoint_name=args.endpoint_name,
            machine_type=args.machine_type,
            accelerator_type=args.accelerator_type,
            accelerator_count=args.accelerator_count,
            min_replica_count=args.min_replicas,
            max_replica_count=args.max_replicas,
            project_id=args.project_id,
            region=args.region
        )
        
        print("\n" + "="*80)
        print("🎉 SUCCESS!")
        print("="*80)
        print("\nNext steps:")
        print(f"1. Add to .env: GCP_ENDPOINT_ID={endpoint_id}")
        print("2. Test endpoint: python scripts/test_endpoint.py")
        print("3. Run Chainlit app: chainlit run src/app/main.py -w")
        print("\n" + "="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
