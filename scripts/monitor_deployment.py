"""
Monitor the deployment status and update .env file when complete.

Usage:
    python scripts/monitor_deployment.py
"""
import os
import time
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")
ENDPOINT_NAME = "nutrition-assistant-endpoint"

aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"\n{'='*80}")
print("📊 Monitoring Deployment Status")
print(f"{'='*80}")
print(f"Endpoint: {ENDPOINT_NAME}")
print(f"Project: {PROJECT_ID}")
print(f"Region: {REGION}")
print(f"{'='*80}\n")

# Get the endpoint
print("🔍 Finding endpoint...")
endpoints = aiplatform.Endpoint.list(
    filter=f'display_name="{ENDPOINT_NAME}"',
    order_by="create_time desc"
)

if not endpoints:
    print("❌ Endpoint not found. Deployment may not have started yet.")
    print("   Wait a moment and try again.")
    exit(1)

endpoint = endpoints[0]
endpoint_id = endpoint.name.split('/')[-1]

print(f"✅ Found endpoint: {endpoint.display_name}")
print(f"   Endpoint ID: {endpoint_id}")
print(f"   Resource: {endpoint.resource_name}")
print(f"\n🔗 Console: https://console.cloud.google.com/vertex-ai/endpoints/{endpoint_id}?project={PROJECT_ID}")

# Check deployed models
print(f"\n{'='*80}")
print("📦 Checking Deployed Models")
print(f"{'='*80}\n")

if not endpoint.gca_resource.deployed_models:
    print("⏳ No models deployed yet. Deployment is still in progress.")
    print("   This typically takes 15-30 minutes.")
    print("\n💡 You can:")
    print("   - Wait and run this script again later")
    print("   - Monitor in console (link above)")
    print("   - Continue with other work - I'll notify when complete")
else:
    print(f"✅ Found {len(endpoint.gca_resource.deployed_models)} deployed model(s)!")
    
    for deployed_model in endpoint.gca_resource.deployed_models:
        print(f"\n   Model: {deployed_model.display_name}")
        print(f"   ID: {deployed_model.id}")
        print(f"   Traffic: {deployed_model.traffic_split}%")
        
        # Check if model is ready
        if hasattr(deployed_model, 'state'):
            print(f"   State: {deployed_model.state}")
    
    # Update .env file
    print(f"\n{'='*80}")
    print("📝 Updating .env File")
    print(f"{'='*80}\n")
    
    env_file = ".env"
    env_lines = []
    endpoint_line = f"GCP_ENDPOINT_ID={endpoint_id}"
    project_number_line = "GCP_PROJECT_NUMBER=432566588992"
    
    # Read existing .env
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Check if already exists
    has_endpoint_id = any("GCP_ENDPOINT_ID" in line for line in env_lines)
    has_project_number = any("GCP_PROJECT_NUMBER" in line for line in env_lines)
    
    # Update or append
    if has_endpoint_id:
        env_lines = [endpoint_line + "\n" if "GCP_ENDPOINT_ID" in line else line for line in env_lines]
        print("✅ Updated existing GCP_ENDPOINT_ID in .env")
    else:
        env_lines.append(endpoint_line + "\n")
        print("✅ Added GCP_ENDPOINT_ID to .env")
    
    if not has_project_number:
        env_lines.append(project_number_line + "\n")
        print("✅ Added GCP_PROJECT_NUMBER to .env")
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print(f"\n{'='*80}")
    print("🎉 Deployment Complete!")
    print(f"{'='*80}\n")
    print("Your .env file has been updated with:")
    print(f"  GCP_ENDPOINT_ID={endpoint_id}")
    print("\nYou can now test your endpoint:")
    print("  python scripts/test_endpoint.py")
    print("\nOr run the Chainlit app:")
    print("  chainlit run src/app/main.py -w")
    print(f"\n{'='*80}\n")

print(f"\n{'='*80}\n")
