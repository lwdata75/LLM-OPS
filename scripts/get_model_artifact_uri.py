"""
Script to get the model artifact URI from the completed pipeline.
"""
import os
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")
PIPELINE_JOB_ID = "nutrition-assistant-training-pipeline-20251021140422"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Get the pipeline job
pipeline_job = aiplatform.PipelineJob.get(
    resource_name=f"projects/432566588992/locations/{REGION}/pipelineJobs/{PIPELINE_JOB_ID}"
)

print(f"\n{'='*80}")
print(f"Pipeline Job: {pipeline_job.display_name}")
print(f"State: {pipeline_job.state}")
print(f"{'='*80}\n")

# Get the task details
task_details = pipeline_job.task_details

print(f"Pipeline has {len(task_details)} tasks:\n")

for task in task_details:
    print(f"Task: {task.task_name}")
    print(f"  State: {task.state}")
    
    # Look for the fine-tuning task outputs
    if "fine-tune" in task.task_name.lower() and task.outputs:
        print(f"  Outputs:")
        for output_name, output_value in task.outputs.items():
            print(f"    {output_name}: {output_value}")
            
            # Try to extract artifact URI
            if hasattr(output_value, 'artifacts') and output_value.artifacts:
                for artifact in output_value.artifacts:
                    if hasattr(artifact, 'uri'):
                        print(f"      Artifact URI: {artifact.uri}")
            elif hasattr(output_value, 'uri'):
                print(f"      URI: {output_value.uri}")
    print()

print(f"\n{'='*80}")
print("GCS Pipeline Root:")
print(f"gs://llmops_101_europ/pipeline_root/{PIPELINE_JOB_ID}/")
print(f"{'='*80}\n")
