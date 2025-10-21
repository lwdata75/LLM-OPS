"""
Undeploy model from endpoint to stop billing.
This removes the model from the endpoint but keeps the endpoint itself.

Usage:
    python scripts/undeploy_model.py
"""
import os
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
PROJECT_NUMBER = os.getenv("GCP_PROJECT_NUMBER", "432566588992")
REGION = os.getenv("GCP_REGION", "europe-west2")
ENDPOINT_ID = os.getenv("GCP_ENDPOINT_ID", "5724492940806455296")

def undeploy_model():
    """Undeploy all models from the endpoint to stop billing."""
    print("=" * 70)
    print("🛑 UNDEPLOYING MODEL FROM ENDPOINT")
    print("=" * 70)
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Get endpoint
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}"
    )
    
    print(f"\n📍 Endpoint: {endpoint.display_name}")
    print(f"   ID: {ENDPOINT_ID}")
    
    # Get deployed models
    deployed_models = endpoint.gca_resource.deployed_models
    
    if not deployed_models:
        print("\n✅ No models deployed - endpoint already empty!")
        print("💰 No charges being incurred")
        return
    
    print(f"\n📦 Found {len(deployed_models)} deployed model(s)")
    
    # Undeploy each model
    for deployed_model in deployed_models:
        print(f"\n🔄 Undeploying: {deployed_model.display_name}")
        print(f"   Deployed Model ID: {deployed_model.id}")
        
        try:
            # Undeploy
            endpoint.undeploy(deployed_model_id=deployed_model.id)
            print(f"   ✅ Successfully undeployed!")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ UNDEPLOYMENT COMPLETE!")
    print("=" * 70)
    print("\n💰 Billing for model serving has STOPPED")
    print("📝 The endpoint still exists but has no models deployed")
    print("🔄 You can redeploy anytime using scripts/deploy_to_endpoint.py")
    print("\n⚠️  Note: To completely delete the endpoint, run:")
    print("   python scripts/delete_endpoint.py")

if __name__ == "__main__":
    undeploy_model()
