"""
Setup script to upload the nutrition dataset to Google Cloud Storage.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import storage
import logging

from src.constants import GCP_PROJECT_ID, GCP_BUCKET_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_dataset_to_gcs():
    """Upload the COMBINED_FOOD_DATASET.csv to GCS bucket."""
    
    # Local file path
    local_file = project_root / "COMBINED_FOOD_DATASET.csv"
    
    if not local_file.exists():
        logger.error(f"❌ Dataset file not found: {local_file}")
        return False
    
    logger.info(f"📂 Found dataset: {local_file}")
    logger.info(f"📦 Uploading to bucket: {GCP_BUCKET_NAME}")
    
    try:
        # Initialize storage client
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        
        # Check if bucket exists
        if not bucket.exists():
            logger.error(f"❌ Bucket '{GCP_BUCKET_NAME}' does not exist!")
            logger.info("Please create the bucket in GCP Console or run:")
            logger.info(f"  gsutil mb -l {GCP_BUCKET_NAME} gs://{GCP_BUCKET_NAME}")
            return False
        
        # Upload file
        blob = bucket.blob("COMBINED_FOOD_DATASET.csv")
        blob.upload_from_filename(str(local_file))
        
        logger.info(f"✅ Successfully uploaded dataset to gs://{GCP_BUCKET_NAME}/COMBINED_FOOD_DATASET.csv")
        
        # Verify upload
        if blob.exists():
            logger.info(f"📊 File size: {blob.size / (1024*1024):.2f} MB")
            logger.info(f"🔗 GCS URI: gs://{GCP_BUCKET_NAME}/COMBINED_FOOD_DATASET.csv")
            return True
        else:
            logger.error("❌ Upload verification failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error uploading dataset: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Dataset Upload Setup")
    logger.info("=" * 80)
    
    success = upload_dataset_to_gcs()
    
    if success:
        logger.info("\n✅ Setup complete! You can now run the pipeline.")
    else:
        logger.info("\n❌ Setup failed. Please fix the errors above.")
        sys.exit(1)
