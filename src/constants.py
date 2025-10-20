"""
Constants module for LLM-OPS project.
Loads configuration from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GCP Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
GCP_REGION = os.getenv("GCP_REGION", "europe-west2")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "llmops_101_europ")

# Data paths
RAW_DATA_GCS_PATH = f"gs://{GCP_BUCKET_NAME}/20-10-2025-08:28:00 - FOOD/COMBINED_FOOD_DATASET.csv"
PROCESSED_DATA_LOCAL_DIR = "data/processed"
TRAIN_DATA_FILENAME = "train_dataset.csv"
TEST_DATA_FILENAME = "test_dataset.csv"

# Model configuration
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Nutrition dataset specific constants
NUTRITION_COLUMNS = [
    'food', 'Caloric Value', 'Fat', 'Saturated Fats', 'Carbohydrates', 
    'Sugars', 'Protein', 'Dietary Fiber', 'Sodium', 'Vitamin C', 
    'Calcium', 'Iron', 'Nutrition Density'
]

# Key nutrition metrics for responses
KEY_MACROS = ['Caloric Value', 'Fat', 'Carbohydrates', 'Protein']

# Validation
def validate_constants():
    """Validate that all required constants are set."""
    missing_vars = []
    
    if not GCP_PROJECT_ID:
        missing_vars.append("GCP_PROJECT_ID")
    if not GCP_BUCKET_NAME:
        missing_vars.append("GCP_BUCKET_NAME")
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

if __name__ == "__main__":
    # Test the constants when running directly
    try:
        validate_constants()
        print("✅ All constants loaded successfully!")
        print(f"   Project ID: {GCP_PROJECT_ID}")
        print(f"   Region: {GCP_REGION}")
        print(f"   Bucket: {GCP_BUCKET_NAME}")
        print(f"   Raw data path: {RAW_DATA_GCS_PATH}")
    except ValueError as e:
        print(f"❌ {e}")