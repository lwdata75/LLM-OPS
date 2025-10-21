"""
Script to find the fine-tuned model artifact URI in GCS.
"""
import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

# Configuration
BUCKET_NAME = "llmops_101_europ"
PIPELINE_JOB_ID = "nutrition-assistant-training-pipeline-20251021140422"
PREFIX = f"pipeline_root/{PIPELINE_JOB_ID}/"

# Initialize GCS client
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

print(f"\n{'='*80}")
print(f"Searching for fine-tuned model in: gs://{BUCKET_NAME}/{PREFIX}")
print(f"{'='*80}\n")

# List all blobs with the prefix
blobs = list(bucket.list_blobs(prefix=PREFIX))

# Look for the fine-tuning component output
model_artifacts = []
for blob in blobs:
    if "fine-tuning-component" in blob.name and "fine_tuned_model" in blob.name:
        model_artifacts.append(blob.name)

if model_artifacts:
    print("Found fine-tuned model artifacts:\n")
    for artifact in sorted(model_artifacts):
        print(f"  gs://{BUCKET_NAME}/{artifact}")
    
    # Find the base directory (without specific files)
    base_paths = set()
    for artifact in model_artifacts:
        # Extract path up to fine_tuned_model directory
        if "fine_tuned_model" in artifact:
            parts = artifact.split("fine_tuned_model")
            if len(parts) >= 2:
                base_path = parts[0] + "fine_tuned_model"
                base_paths.add(base_path)
    
    print(f"\n{'='*80}")
    print("Model Base Directory (use this for registration):")
    print(f"{'='*80}\n")
    for base_path in sorted(base_paths):
        model_uri = f"gs://{BUCKET_NAME}/{base_path}"
        print(f"  {model_uri}")
        print(f"\n  Save this URI for model registration!")
else:
    print("❌ No fine-tuned model artifacts found.")
    print("\nShowing first 20 files in pipeline root:")
    for i, blob in enumerate(blobs[:20]):
        print(f"  {blob.name}")

print(f"\n{'='*80}\n")
