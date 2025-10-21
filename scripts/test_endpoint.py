"""
Script to test the Vertex AI endpoint with a sample request.

Usage:
    python scripts/test_endpoint.py --prompt "What are the benefits of spinach?"
"""
import os
import argparse
import subprocess
import requests
import json
from dotenv import load_dotenv

load_dotenv()


def get_access_token() -> str:
    """Get GCP access token using gcloud CLI."""
    try:
        access_token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True
        ).strip()
        return access_token
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        print("Make sure gcloud CLI is installed and authenticated:")
        print("  gcloud auth login")
        raise


def test_endpoint(prompt: str, endpoint_id: str = None) -> dict:
    """
    Test the Vertex AI endpoint with a sample prompt.
    
    Args:
        prompt: User's input text
        endpoint_id: Optional endpoint ID (uses env var if not provided)
        
    Returns:
        Response dictionary from the endpoint
    """
    # Get configuration
    project_number = os.getenv("GCP_PROJECT_NUMBER", "432566588992")
    region = os.getenv("GCP_REGION", "europe-west2")
    
    if endpoint_id is None:
        endpoint_id = os.getenv("GCP_ENDPOINT_ID")
    
    if not endpoint_id:
        raise ValueError(
            "Endpoint ID not found. Set GCP_ENDPOINT_ID in .env file or pass --endpoint-id"
        )
    
    # Get access token
    print("🔐 Getting access token...")
    access_token = get_access_token()
    
    # Build endpoint URL
    endpoint_url = (
        f"https://{region}-aiplatform.googleapis.com/v1/"
        f"projects/{project_number}/locations/{region}/"
        f"endpoints/{endpoint_id}:predict"
    )
    
    print(f"\n{'='*80}")
    print(f"📡 Testing Endpoint")
    print(f"{'='*80}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"Region: {region}")
    print(f"Prompt: {prompt}")
    print(f"{'='*80}\n")
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "instances": [
            {"prompt": prompt}
        ],
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    
    # Send request
    print("📤 Sending request...")
    try:
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        print("\n✅ Response received!")
        print(f"\n{'='*80}")
        print("📥 Model Response")
        print(f"{'='*80}\n")
        
        if "predictions" in result and len(result["predictions"]) > 0:
            prediction = result["predictions"][0]
            
            if "error" in prediction:
                print(f"⚠️ Error: {prediction['error']}")
            elif "generated_text" in prediction:
                print(prediction["generated_text"])
            else:
                print(json.dumps(prediction, indent=2))
        else:
            print(json.dumps(result, indent=2))
        
        print(f"\n{'='*80}\n")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Test Vertex AI endpoint with a sample request"
    )
    parser.add_argument(
        "--prompt",
        default="What are the nutritional benefits of spinach?",
        help="Prompt to send to the model"
    )
    parser.add_argument(
        "--endpoint-id",
        default=None,
        help="Endpoint ID (uses GCP_ENDPOINT_ID from .env if not provided)"
    )
    
    args = parser.parse_args()
    
    try:
        result = test_endpoint(args.prompt, args.endpoint_id)
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
