"""
Data processing module for Yoda sentence dataset.
Converts the dataset to conversational format for Phi-3 fine-tuning.
"""

import os
import sys
import pandas as pd
import datasets
from typing import Tuple, List, Dict, Any
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.constants import (
    RAW_DATA_GCS_PATH, 
    PROCESSED_DATA_LOCAL_DIR, 
    TRAIN_DATA_FILENAME, 
    TEST_DATA_FILENAME,
    TEST_SIZE,
    RANDOM_STATE
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_dataset_from_gcs(gcs_path: str) -> pd.DataFrame:
    """
    Load the Yoda sentences dataset from Google Cloud Storage.
    
    Args:
        gcs_path (str): GCS path to the CSV file (gs://bucket/path/file.csv)
    
    Returns:
        pd.DataFrame: Raw dataset
    """
    logger.info(f"Loading dataset from {gcs_path}")
    
    try:
        df = pd.read_csv(gcs_path)
        logger.info(f"Successfully loaded dataset with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Failed to load dataset from GCS: {str(e)}")
        raise

def format_to_conversational(df: pd.DataFrame, use_extra_translation: bool = True) -> List[Dict[str, Any]]:
    """
    Convert the Yoda dataset to conversational format for SFTTrainer.
    
    Args:
        df (pd.DataFrame): Raw dataset with columns: sentence, translation, translation_extra
        use_extra_translation (bool): Whether to use translation_extra or translation column
    
    Returns:
        List[Dict]: List of conversations in the format expected by SFTTrainer
    """
    logger.info(f"Converting {len(df)} rows to conversational format")
    
    conversations = []
    translation_column = "translation_extra" if use_extra_translation else "translation"
    
    if translation_column not in df.columns:
        logger.warning(f"Column '{translation_column}' not found. Available columns: {list(df.columns)}")
        translation_column = "translation"  # Fallback to basic translation
    
    for _, row in df.iterrows():
        conversation = [
            {
                "role": "user",
                "content": row["sentence"]
            },
            {
                "role": "assistant", 
                "content": row[translation_column]
            }
        ]
        conversations.append({"messages": conversation})
    
    logger.info(f"Successfully created {len(conversations)} conversations")
    return conversations

def convert_to_hf_dataset(conversations: List[Dict[str, Any]]) -> datasets.Dataset:
    """
    Convert the conversation list to a Hugging Face Dataset.
    
    Args:
        conversations (List[Dict]): List of conversations
    
    Returns:
        datasets.Dataset: Hugging Face dataset
    """
    logger.info("Converting conversations to Hugging Face Dataset")
    
    # Convert to DataFrame first
    df = pd.DataFrame(conversations)
    
    # Convert to Hugging Face Dataset
    hf_dataset = datasets.Dataset.from_pandas(df)
    
    logger.info(f"Created Hugging Face dataset with {len(hf_dataset)} examples")
    return hf_dataset

def split_dataset(dataset: datasets.Dataset, test_size: float = TEST_SIZE, random_state: int = RANDOM_STATE) -> Tuple[datasets.Dataset, datasets.Dataset]:
    """
    Split the dataset into training and test sets.
    
    Args:
        dataset (datasets.Dataset): Full dataset
        test_size (float): Proportion of test set (default: 0.2)
        random_state (int): Random seed for reproducibility
    
    Returns:
        Tuple[datasets.Dataset, datasets.Dataset]: (train_dataset, test_dataset)
    """
    logger.info(f"Splitting dataset with test_size={test_size}, random_state={random_state}")
    
    split_dataset = dataset.train_test_split(test_size=test_size, seed=random_state)
    train_dataset = split_dataset["train"]
    test_dataset = split_dataset["test"]
    
    logger.info(f"Train set: {len(train_dataset)} examples")
    logger.info(f"Test set: {len(test_dataset)} examples")
    
    return train_dataset, test_dataset

def save_datasets_locally(train_dataset: datasets.Dataset, test_dataset: datasets.Dataset, output_dir: str = PROCESSED_DATA_LOCAL_DIR) -> Tuple[str, str]:
    """
    Save the processed datasets to local JSON files (better for nested data).
    
    Args:
        train_dataset (datasets.Dataset): Training dataset
        test_dataset (datasets.Dataset): Test dataset
        output_dir (str): Output directory for JSON files
    
    Returns:
        Tuple[str, str]: (train_file_path, test_file_path)
    """
    logger.info(f"Saving datasets to {output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define file paths (use .json extension)
    train_file_path = os.path.join(output_dir, "train_dataset.json")
    test_file_path = os.path.join(output_dir, "test_dataset.json")
    
    # Save as JSON (better for nested structures)
    train_dataset.to_json(train_file_path)
    test_dataset.to_json(test_file_path)
    
    logger.info(f"Saved train dataset to: {train_file_path}")
    logger.info(f"Saved test dataset to: {test_file_path}")
    
    return train_file_path, test_file_path

def process_yoda_dataset(gcs_path: str = RAW_DATA_GCS_PATH, use_extra_translation: bool = True) -> Tuple[str, str]:
    """
    Complete data processing pipeline for the Yoda sentences dataset.
    
    Args:
        gcs_path (str): GCS path to the raw CSV file
        use_extra_translation (bool): Whether to use translation_extra or translation column
    
    Returns:
        Tuple[str, str]: (train_file_path, test_file_path)
    """
    logger.info("Starting Yoda dataset processing pipeline")
    
    try:
        # Step 1: Load dataset from GCS
        raw_df = load_dataset_from_gcs(gcs_path)
        
        # Step 2: Format to conversational format
        conversations = format_to_conversational(raw_df, use_extra_translation)
        
        # Step 3: Convert to Hugging Face Dataset
        hf_dataset = convert_to_hf_dataset(conversations)
        
        # Step 4: Split into train/test
        train_dataset, test_dataset = split_dataset(hf_dataset)
        
        # Step 5: Save locally
        train_file_path, test_file_path = save_datasets_locally(train_dataset, test_dataset)
        
        logger.info("✅ Data processing pipeline completed successfully!")
        return train_file_path, test_file_path
        
    except Exception as e:
        logger.error(f"❌ Data processing pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the data processing pipeline when script is executed directly
    try:
        train_path, test_path = process_yoda_dataset()
        print(f"\n🎉 Processing complete!")
        print(f"📁 Train dataset saved to: {train_path}")
        print(f"📁 Test dataset saved to: {test_path}")
        
        # Show a preview of the processed data
        print(f"\n📊 Preview of processed data:")
        import json
        with open(train_path, 'r') as f:
            train_data = [json.loads(line) for line in f.readlines()[:3]]
        
        print(f"Train dataset examples: {len(train_data)}")
        for i, example in enumerate(train_data):
            print(f"\nExample {i+1}:")
            for msg in example['messages']:
                print(f"  {msg['role'].upper()}: {msg['content']}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")