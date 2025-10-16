"""
Check pipeline status and verify outputs.
"""

import os
import sys
from dotenv import load_dotenv
from google.cloud import aiplatform, storage

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "europe-west2")
BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")

def check_pipeline_status(job_id: str):
    """Check the status of a pipeline job."""
    print(f"🔍 Checking pipeline status for job: {job_id}")
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    try:
        # Get the pipeline job
        job = aiplatform.PipelineJob.get(job_id)
        
        print(f"📊 Pipeline Status: {job.state}")
        print(f"📝 Display Name: {job.display_name}")
        print(f"🕐 Create Time: {job.create_time}")
        
        if job.state == "PIPELINE_STATE_SUCCEEDED":
            print("✅ Pipeline completed successfully!")
            return True
        elif job.state == "PIPELINE_STATE_RUNNING":
            print("⏳ Pipeline is still running...")
            return False
        elif job.state == "PIPELINE_STATE_FAILED":
            print("❌ Pipeline failed!")
            print(f"Error: {job.error}")
            return False
        else:
            print(f"ℹ️ Pipeline state: {job.state}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking pipeline status: {str(e)}")
        return False

def check_gcs_outputs():
    """Check for output files in GCS bucket."""
    print(f"📁 Checking for outputs in gs://{BUCKET_NAME}/processed_data/")
    
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        
        # List files in processed_data directory
        blobs = list(bucket.list_blobs(prefix="processed_data/"))
        
        if blobs:
            print(f"✅ Found {len(blobs)} files in processed_data/:")
            for blob in blobs:
                print(f"   📄 {blob.name} (size: {blob.size} bytes)")
            return True
        else:
            print("❌ No files found in processed_data/ directory")
            return False
            
    except Exception as e:
        print(f"❌ Error checking GCS outputs: {str(e)}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🔍 Pipeline Status Checker")
    print("=" * 60)
    
    # The job ID from the previous run
    job_id = "projects/432566588992/locations/europe-west2/pipelineJobs/yoda-data-preprocessing-pipeline-20251016135008"
    
    # Check pipeline status
    pipeline_success = check_pipeline_status(job_id)
    
    print()
    
    # Check GCS outputs
    outputs_exist = check_gcs_outputs()
    
    print("\n" + "=" * 60)
    if pipeline_success and outputs_exist:
        print("🎉 Pipeline completed successfully with outputs!")
    elif pipeline_success:
        print("✅ Pipeline completed but checking outputs...")
    else:
        print("⏳ Pipeline may still be running or failed")
    print("=" * 60)

if __name__ == "__main__":
    main()