"""
Script to check the status of running pipelines in Vertex AI.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import aiplatform
import logging

from src.constants import GCP_PROJECT_ID, GCP_REGION, PIPELINE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_pipeline_status(limit: int = 5):
    """Check the status of recent pipeline runs.
    
    Args:
        limit: Number of recent pipelines to display
    """
    logger.info(f"Checking pipeline status for project: {GCP_PROJECT_ID}")
    
    # Initialize Vertex AI
    aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
    
    # List pipeline jobs
    jobs = aiplatform.PipelineJob.list(
        filter=f'display_name:"{PIPELINE_NAME}*"',
        order_by="create_time desc",
    )
    
    logger.info(f"\n📊 Recent Pipeline Runs (last {limit}):\n")
    logger.info("=" * 100)
    
    count = 0
    for job in jobs:
        if count >= limit:
            break
            
        logger.info(f"\nPipeline: {job.display_name}")
        logger.info(f"  State: {job.state.name}")
        logger.info(f"  Created: {job.create_time}")
        logger.info(f"  Updated: {job.update_time}")
        logger.info(f"  Resource Name: {job.resource_name}")
        
        if job.state.name == "PIPELINE_STATE_SUCCEEDED":
            logger.info(f"  ✅ Status: Completed successfully")
        elif job.state.name == "PIPELINE_STATE_RUNNING":
            logger.info(f"  ⏳ Status: Running...")
        elif job.state.name == "PIPELINE_STATE_FAILED":
            logger.info(f"  ❌ Status: Failed")
            try:
                if hasattr(job, 'error') and job.error:
                    logger.info(f"  Error: {job.error}")
            except:
                pass
        elif job.state.name == "PIPELINE_STATE_PENDING":
            logger.info(f"  🕐 Status: Pending...")
        
        # Console link
        job_id = job.resource_name.split("/")[-1]
        console_url = f"https://console.cloud.google.com/vertex-ai/pipelines/runs/{job_id}?project={GCP_PROJECT_ID}"
        logger.info(f"  🔗 Console: {console_url}")
        logger.info("-" * 100)
        
        count += 1
    
    if count == 0:
        logger.info("No pipeline runs found.")
    
    return jobs


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check pipeline status in Vertex AI")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of recent pipelines to display"
    )
    
    args = parser.parse_args()
    
    check_pipeline_status(limit=args.limit)
