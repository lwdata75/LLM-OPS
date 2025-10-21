"""
Get detailed error logs from a failed pipeline run.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import aiplatform
import logging

from src.constants import GCP_PROJECT_ID, GCP_REGION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_pipeline_details(job_id: str = None):
    """Get detailed information about a pipeline run."""
    
    aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
    
    if job_id:
        # Get specific job
        job = aiplatform.PipelineJob.get(
            resource_name=f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/pipelineJobs/{job_id}"
        )
    else:
        # Get latest job
        jobs = list(aiplatform.PipelineJob.list(order_by="create_time desc"))
        if not jobs:
            logger.error("No pipeline jobs found")
            return
        job = jobs[0]
    
    logger.info("=" * 80)
    logger.info(f"Pipeline: {job.display_name}")
    logger.info(f"State: {job.state.name}")
    logger.info(f"Created: {job.create_time}")
    logger.info(f"Updated: {job.update_time}")
    logger.info("=" * 80)
    
    # Get task details
    logger.info("\n📋 TASK DETAILS:\n")
    
    try:
        task_details = job.task_details
        
        for task in task_details:
            logger.info(f"\nTask: {task.task_name}")
            logger.info(f"  State: {task.state}")
            logger.info(f"  Start: {task.start_time}")
            logger.info(f"  End: {task.end_time}")
            
            if task.state.name in ["STATE_FAILED", "FAILED"]:
                logger.info(f"  ❌ FAILED TASK FOUND!")
                
                # Try to get error information
                if hasattr(task, 'error') and task.error:
                    logger.info(f"  Error: {task.error}")
                
                if hasattr(task, 'execution'):
                    logger.info(f"  Execution: {task.execution}")
                    
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Error getting task details: {e}")
    
    # Get job details
    logger.info("\n📊 JOB DETAILS:\n")
    logger.info(f"Job Resource Name: {job.resource_name}")
    logger.info(f"Pipeline Spec URI: {job.pipeline_spec_uri if hasattr(job, 'pipeline_spec_uri') else 'N/A'}")
    
    # Get GCS bucket info
    logger.info("\n📦 ARTIFACTS:\n")
    logger.info(f"GCS Root: {job.pipeline_spec.get('defaultPipelineRoot', 'N/A') if hasattr(job, 'pipeline_spec') else 'N/A'}")
    
    # Console URL
    job_id = job.resource_name.split("/")[-1]
    console_url = f"https://console.cloud.google.com/vertex-ai/pipelines/runs/{job_id}?project={GCP_PROJECT_ID}"
    logger.info(f"\n🔗 View in Console: {console_url}")
    
    logger.info("\n" + "=" * 80)
    logger.info("💡 TIP: Check the GCP Console for detailed logs and error messages")
    logger.info("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get detailed pipeline error information")
    parser.add_argument("--job-id", help="Specific job ID to check")
    
    args = parser.parse_args()
    
    get_pipeline_details(job_id=args.job_id)
