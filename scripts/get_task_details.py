"""
Get detailed task information from the pipeline job.
"""
import os
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import PipelineServiceClient
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "aerobic-polygon-460910-v9"
REGION = "europe-west2"
PIPELINE_JOB_ID = "nutrition-assistant-training-pipeline-20251021140422"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Get pipeline job
client = PipelineServiceClient(
    client_options={"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
)

pipeline_resource_name = f"projects/432566588992/locations/{REGION}/pipelineJobs/{PIPELINE_JOB_ID}"

pipeline_job = client.get_pipeline_job(name=pipeline_resource_name)

print(f"\n{'='*80}")
print(f"Pipeline: {pipeline_job.display_name}")
print(f"State: {pipeline_job.state.name}")
print(f"{'='*80}\n")

# Get job details
job_detail = pipeline_job.job_detail

if job_detail and job_detail.task_details:
    print(f"Found {len(job_detail.task_details)} tasks:\n")
    
    for task in job_detail.task_details:
        print(f"\nTask: {task.task_name}")
        print(f"Task ID: {task.task_id}")
        print(f"State: {task.state.name}")
        
        # Check outputs
        if task.outputs:
            print(f"Outputs:")
            for key, value in task.outputs.items():
                print(f"  {key}:")
                # Try to get artifact info
                if hasattr(value, 'artifacts'):
                    for artifact in value.artifacts:
                        if hasattr(artifact, 'uri'):
                            print(f"    URI: {artifact.uri}")
                        if hasattr(artifact, 'metadata'):
                            print(f"    Metadata: {artifact.metadata}")
                elif hasattr(value, 'uri'):
                    print(f"    URI: {value.uri}")
                else:
                    print(f"    Value: {str(value)[:200]}")
        
        # Check inputs
        if task.inputs and "fine-tune" in task.task_name.lower():
            print(f"Inputs:")
            for key, value in task.inputs.items():
                print(f"  {key}: {str(value)[:200]}")
                
print(f"\n{'='*80}\n")
