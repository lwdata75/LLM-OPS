"""
Chainlit web application for interacting with the deployed nutrition assistant model.

This app connects to a Vertex AI endpoint and allows users to chat with the fine-tuned
Phi-3 model for nutrition-related questions.

To run:
    chainlit run src/app/main.py -w
"""
import os
import re
import subprocess
import requests
from typing import Dict, Any
import chainlit as cl
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth

load_dotenv()

# Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
GCP_PROJECT_NUMBER = os.getenv("GCP_PROJECT_NUMBER", "432566588992")
GCP_REGION = os.getenv("GCP_REGION", "europe-west2")
GCP_ENDPOINT_ID = os.getenv("GCP_ENDPOINT_ID", "")  # Set this after deploying to endpoint


def get_access_token() -> str:
    """
    Get GCP access token using Application Default Credentials or gcloud CLI.
    
    Returns:
        Access token string
    """
    try:
        # Try using Application Default Credentials first
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e1:
        # Fallback to gcloud CLI
        try:
            access_token = subprocess.check_output(
                ["gcloud", "auth", "print-access-token"],
                text=True
            ).strip()
            return access_token
        except Exception as e2:
            print(f"Error getting access token with ADC: {e1}")
            print(f"Error getting access token with gcloud: {e2}")
            raise Exception(
                "Could not authenticate. Please run: gcloud auth application-default login"
            )


def build_endpoint_url() -> str:
    """
    Build the Vertex AI endpoint URL.
    
    Returns:
        Full endpoint URL
    """
    if not GCP_ENDPOINT_ID:
        raise ValueError(
            "GCP_ENDPOINT_ID not set in .env file. "
            "Please deploy your model to an endpoint first and set the endpoint ID."
        )
    
    url = (
        f"https://{GCP_REGION}-aiplatform.googleapis.com/v1/"
        f"projects/{GCP_PROJECT_NUMBER}/locations/{GCP_REGION}/"
        f"endpoints/{GCP_ENDPOINT_ID}:predict"
    )
    return url


def extract_assistant_response(generated_text: str) -> str:
    """
    Extract the assistant's response from the model output.
    
    Args:
        generated_text: Full generated text from the model
        
    Returns:
        Cleaned assistant response
    """
    # Try to extract text after assistant marker
    assistant_pattern = r"<\|assistant\|>\s*(.*?)(?:<\|end\||$)"
    match = re.search(assistant_pattern, generated_text, re.DOTALL)
    
    if match:
        response = match.group(1).strip()
        return response
    
    # Fallback: return the generated text as-is
    return generated_text.strip()


async def call_vertex_ai_endpoint(user_message: str) -> str:
    """
    Send a prediction request to the Vertex AI endpoint.
    
    Args:
        user_message: User's input message
        
    Returns:
        Model's response text
    """
    try:
        # Get access token
        access_token = get_access_token()
        
        # Build endpoint URL
        endpoint_url = build_endpoint_url()
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [
                {"prompt": user_message}
            ],
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        # Send request
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Check response
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        if "predictions" in result and len(result["predictions"]) > 0:
            prediction = result["predictions"][0]
            
            if "error" in prediction:
                return f"⚠️ Error from model: {prediction['error']}"
            
            if "generated_text" in prediction:
                return extract_assistant_response(prediction["generated_text"])
        
        return "⚠️ Unexpected response format from the model."
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error calling endpoint: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@cl.on_chat_start
async def start():
    """
    Initialize the chat session.
    """
    # Check if endpoint is configured
    if not GCP_ENDPOINT_ID:
        await cl.Message(
            content=(
                "⚠️ **Configuration Required**\n\n"
                "The Vertex AI endpoint is not configured. Please:\n"
                "1. Deploy your model to a Vertex AI endpoint\n"
                "2. Set `GCP_ENDPOINT_ID` in your `.env` file\n"
                "3. Restart the application\n\n"
                "See `session4_practice.md` for deployment instructions."
            )
        ).send()
        return
    
    # Welcome message
    await cl.Message(
        content=(
            "# 🥗 Nutrition Assistant\n\n"
            f"Welcome! I'm a fine-tuned Phi-3 model specialized in nutrition questions.\n\n"
            "**Connected to:**\n"
            f"- Project: `{GCP_PROJECT_ID}`\n"
            f"- Region: `{GCP_REGION}`\n"
            f"- Endpoint: `{GCP_ENDPOINT_ID}`\n\n"
            "Ask me anything about nutrition, food, calories, or healthy eating! 🍎"
        )
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Process user messages and get responses from the model.
    
    Args:
        message: User's input message
    """
    # Check if endpoint is configured
    if not GCP_ENDPOINT_ID:
        await cl.Message(
            content="⚠️ Endpoint not configured. Please set GCP_ENDPOINT_ID in .env file."
        ).send()
        return
    
    # Show thinking indicator
    async with cl.Step(name="Thinking...") as step:
        step.output = "Sending your question to the nutrition assistant..."
        
        # Call the endpoint
        response_text = await call_vertex_ai_endpoint(message.content)
        
        step.output = "Got response from the model!"
    
    # Send the response
    await cl.Message(content=response_text).send()


# Settings for Chainlit
@cl.set_starters
async def set_starters():
    """
    Set starter prompts for the chat.
    """
    return [
        cl.Starter(
            label="Spinach nutrition",
            message="What are the nutritional benefits of spinach?",
            icon="🥬"
        ),
        cl.Starter(
            label="High protein foods",
            message="What are some high-protein foods?",
            icon="🍗"
        ),
        cl.Starter(
            label="Vitamin C sources",
            message="Which foods are rich in vitamin C?",
            icon="🍊"
        ),
        cl.Starter(
            label="Healthy snacks",
            message="Can you suggest some healthy snack options?",
            icon="🥜"
        ),
    ]
