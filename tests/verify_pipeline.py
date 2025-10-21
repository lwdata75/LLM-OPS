"""
Complete verification and status check for the nutrition training pipeline.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from google.cloud import aiplatform, storage
from src.constants import GCP_PROJECT_ID, GCP_REGION, GCP_BUCKET_NAME, PIPELINE_NAME
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_header(text):
    """Print a formatted header."""
    logger.info("\n" + "=" * 80)
    logger.info(text.center(80))
    logger.info("=" * 80)


def check_environment():
    """Verify environment setup."""
    print_header("🔧 ENVIRONMENT CHECK")
    
    checks = {
        "GCP_PROJECT_ID": GCP_PROJECT_ID,
        "GCP_REGION": GCP_REGION,
        "GCP_BUCKET_NAME": GCP_BUCKET_NAME,
    }
    
    all_good = True
    for key, value in checks.items():
        if value:
            logger.info(f"✅ {key}: {value}")
        else:
            logger.info(f"❌ {key}: NOT SET")
            all_good = False
    
    return all_good


def check_gcs_data():
    """Check if dataset is in GCS."""
    print_header("📦 DATA CHECK")
    
    try:
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob("COMBINED_FOOD_DATASET.csv")
        
        if blob.exists():
            logger.info(f"✅ Dataset found in GCS")
            logger.info(f"   URI: gs://{GCP_BUCKET_NAME}/COMBINED_FOOD_DATASET.csv")
            logger.info(f"   Size: {blob.size / (1024*1024):.2f} MB")
            return True
        else:
            logger.info(f"❌ Dataset NOT found in GCS")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking GCS: {e}")
        return False


def check_pipeline_status():
    """Check current pipeline runs."""
    print_header("🚀 PIPELINE STATUS")
    
    try:
        aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        
        jobs = list(aiplatform.PipelineJob.list(
            filter=f'display_name:"{PIPELINE_NAME}*"',
            order_by="create_time desc",
        ))
        
        if not jobs:
            logger.info("ℹ️  No pipeline runs found yet")
            return None
        
        latest_job = jobs[0]
        logger.info(f"📊 Latest Pipeline: {latest_job.display_name}")
        logger.info(f"   Status: {latest_job.state.name}")
        logger.info(f"   Created: {latest_job.create_time}")
        
        if latest_job.state.name == "PIPELINE_STATE_RUNNING":
            logger.info("   ⏳ Pipeline is currently RUNNING")
            logger.info(f"   🔗 Monitor: https://console.cloud.google.com/vertex-ai/pipelines?project={GCP_PROJECT_ID}")
        elif latest_job.state.name == "PIPELINE_STATE_SUCCEEDED":
            logger.info("   ✅ Pipeline COMPLETED successfully!")
        elif latest_job.state.name == "PIPELINE_STATE_FAILED":
            logger.info("   ❌ Pipeline FAILED")
            if latest_job.error:
                logger.info(f"   Error: {latest_job.error}")
        elif latest_job.state.name == "PIPELINE_STATE_PENDING":
            logger.info("   🕐 Pipeline is PENDING...")
        
        return latest_job
        
    except Exception as e:
        logger.error(f"❌ Error checking pipeline: {e}")
        return None


def check_components():
    """Check if all component files exist."""
    print_header("📁 COMPONENT FILES")
    
    components = [
        "src/constants.py",
        "src/pipeline_components/data_transformation_component.py",
        "src/pipeline_components/fine_tuning_component.py",
        "src/pipeline_components/inference_component.py",
        "src/pipeline_components/evaluation_component.py",
        "src/pipelines/model_training_pipeline.py",
        "scripts/pipeline_runner.py",
        "scripts/check_pipeline_status.py",
    ]
    
    all_exist = True
    for component in components:
        path = project_root / component
        if path.exists() and path.stat().st_size > 0:
            logger.info(f"✅ {component}")
        else:
            logger.info(f"❌ {component} (missing or empty)")
            all_exist = False
    
    return all_exist


def print_summary(env_ok, data_ok, components_ok, pipeline_job):
    """Print final summary."""
    print_header("📋 SUMMARY")
    
    logger.info(f"Environment Setup:   {'✅ OK' if env_ok else '❌ ISSUES'}")
    logger.info(f"Dataset in GCS:      {'✅ OK' if data_ok else '❌ MISSING'}")
    logger.info(f"Component Files:     {'✅ OK' if components_ok else '❌ INCOMPLETE'}")
    logger.info(f"Pipeline Status:     {'✅ RUNNING' if pipeline_job and pipeline_job.state.name == 'PIPELINE_STATE_RUNNING' else '⚠️  CHECK ABOVE'}")
    
    print_header("🎯 QUICK COMMANDS")
    
    logger.info("\n📊 Monitor pipeline:")
    logger.info("   python scripts/check_pipeline_status.py")
    
    logger.info("\n🚀 Submit new pipeline:")
    logger.info("   python scripts/pipeline_runner.py")
    
    logger.info("\n🔍 Validate GCP:")
    logger.info("   python scripts/validate_gcp_setup.py")
    
    logger.info("\n📦 Upload dataset:")
    logger.info("   python scripts/upload_dataset.py")
    
    if pipeline_job and pipeline_job.state.name == "PIPELINE_STATE_RUNNING":
        print_header("⏳ YOUR PIPELINE IS RUNNING!")
        logger.info("\n🔗 View in GCP Console:")
        logger.info(f"   https://console.cloud.google.com/vertex-ai/pipelines?project={GCP_PROJECT_ID}")
        logger.info("\n⏱️  Expected completion time: ~1.5-2 hours")
        logger.info("   Step 1: Data Transformation (5-10 min)")
        logger.info("   Step 2: Fine-Tuning (45-90 min) ⚠️ Longest step")
        logger.info("   Step 3: Inference (10-15 min)")
        logger.info("   Step 4: Evaluation (5 min)")
        logger.info("\n☕ Take a break and check back later!")


def main():
    """Run complete verification."""
    print_header("🔍 NUTRITION PIPELINE VERIFICATION")
    
    env_ok = check_environment()
    data_ok = check_gcs_data()
    components_ok = check_components()
    pipeline_job = check_pipeline_status()
    
    print_summary(env_ok, data_ok, components_ok, pipeline_job)
    
    logger.info("\n" + "=" * 80)
    logger.info("Verification Complete!".center(80))
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    main()
