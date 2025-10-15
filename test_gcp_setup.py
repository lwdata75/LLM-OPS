"""
GCP Setup Test Script
This script tests the connection to Google Cloud Platform services.
"""

import os
from dotenv import load_dotenv
from google.cloud import aiplatform, storage

# Load environment variables from .env file
load_dotenv()

def test_gcp_setup():
    """Test GCP setup by verifying environment variables and API connections."""
    
    print("=" * 60)
    print("Testing GCP Setup")
    print("=" * 60)
    
    # Step 1: Load environment variables
    print("\n1. Loading environment variables...")
    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION")
    bucket_name = os.getenv("GCP_BUCKET_NAME")
    
    if not all([project_id, region, bucket_name]):
        print("❌ Error: Missing environment variables!")
        print(f"   GCP_PROJECT_ID: {project_id or 'NOT SET'}")
        print(f"   GCP_REGION: {region or 'NOT SET'}")
        print(f"   GCP_BUCKET_NAME: {bucket_name or 'NOT SET'}")
        print("\nPlease check your .env file and ensure all variables are set.")
        return False
    
    print(f"   ✅ GCP_PROJECT_ID: {project_id}")
    print(f"   ✅ GCP_REGION: {region}")
    print(f"   ✅ GCP_BUCKET_NAME: {bucket_name}")
    
    # Step 2: Test Vertex AI initialization
    print("\n2. Testing Vertex AI connection...")
    try:
        aiplatform.init(project=project_id, location=region)
        print(f"   ✅ Successfully initialized Vertex AI client")
        print(f"      Project: {project_id}")
        print(f"      Location: {region}")
    except Exception as e:
        print(f"   ❌ Failed to initialize Vertex AI: {str(e)}")
        print("   Make sure you have:")
        print("   - Authenticated with 'gcloud auth login'")
        print("   - Enabled the Vertex AI API")
        print("   - Set the correct project with 'gcloud config set project PROJECT_ID'")
        return False
    
    # Step 3: Test GCS bucket access
    print("\n3. Testing Google Cloud Storage access...")
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        
        # Check if bucket exists
        if bucket.exists():
            print(f"   ✅ Successfully connected to bucket: {bucket_name}")
            
            # List bucket contents
            blobs = list(bucket.list_blobs(max_results=5))
            if blobs:
                print(f"   📁 Found {len(blobs)} file(s) in the bucket (showing max 5):")
                for blob in blobs:
                    print(f"      - {blob.name}")
            else:
                print("   📁 Bucket is empty (no files found)")
        else:
            print(f"   ⚠️  Bucket '{bucket_name}' does not exist or you don't have access to it.")
            print("   Please create the bucket in the GCP console or check your permissions.")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to access GCS bucket: {str(e)}")
        print("   Make sure you have:")
        print("   - Authenticated with 'gcloud auth login'")
        print("   - Enabled the Cloud Storage API")
        print("   - Created the bucket in GCP console")
        print("   - Proper permissions to access the bucket")
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Your GCP setup is working correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_gcp_setup()
