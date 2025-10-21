"""
Completely delete the endpoint to stop all billing.

WARNING: This will permanently delete the endpoint.
You will need to recreate it to deploy models again.

Usage:
    python scripts/delete_endpoint.py
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

def delete_endpoint():
    """Completely delete the endpoint."""
    print("=" * 70)
    print("⚠️  WARNING: ENDPOINT DELETION")
    print("=" * 70)
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Get endpoint
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}"
    )
    
    print(f"\n📍 Endpoint: {endpoint.display_name}")
    print(f"   ID: {ENDPOINT_ID}")
    
    # Confirm deletion
    print("\n⚠️  This will PERMANENTLY DELETE the endpoint!")
    print("   You will need to recreate it to deploy models again.")
    
    confirm = input("\n❓ Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("\n❌ Deletion cancelled")
        return
    
    print("\n🗑️  Deleting endpoint...")
    
    try:
        endpoint.delete(force=True)
        print("\n✅ Endpoint deleted successfully!")
        print("\n💰 All billing stopped")
        print("📝 You can create a new endpoint anytime using scripts/deploy_to_endpoint.py")
    except Exception as e:
        print(f"\n❌ Error deleting endpoint: {e}")

if __name__ == "__main__":
    delete_endpoint()
