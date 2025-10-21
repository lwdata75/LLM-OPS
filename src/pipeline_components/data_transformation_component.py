"""
Data transformation component for the nutrition assistant pipeline.
Converts the food dataset to conversational format for Phi-3 fine-tuning.
"""
from kfp.dsl import component, Output, Dataset
from typing import Dict


@component(
    base_image="python:3.11-slim",
    packages_to_install=[
        "pandas==2.2.3",
        "datasets==3.1.0",
        "gcsfs==2024.9.0",
        "google-cloud-storage==2.18.2",
    ],
)
def data_transformation_component(
    gcs_data_uri: str,
    train_test_split: float,
    train_dataset: Output[Dataset],
    test_dataset: Output[Dataset],
) -> Dict[str, int]:
    """Transform nutrition data into conversational format for Phi-3 fine-tuning.
    
    Args:
        gcs_data_uri: GCS URI to the raw CSV dataset
        train_test_split: Ratio for train/test split (e.g., 0.8)
        train_dataset: Output path for training dataset
        test_dataset: Output path for test dataset
        
    Returns:
        Dictionary with dataset statistics
    """
    import pandas as pd
    import json
    import logging
    from datasets import Dataset
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Loading data from {gcs_data_uri}")
    
    # Load the dataset from GCS
    df = pd.read_csv(gcs_data_uri)
    logger.info(f"Loaded {len(df)} food items")
    
    # Create conversational format
    conversations = []
    for _, row in df.iterrows():
        food_name = row['food']
        
        # Build nutritional information string
        nutrition_info = []
        if pd.notna(row.get('Caloric Value')):
            nutrition_info.append(f"Calories: {row['Caloric Value']} kcal")
        if pd.notna(row.get('Protein')):
            nutrition_info.append(f"Protein: {row['Protein']}g")
        if pd.notna(row.get('Fat')):
            nutrition_info.append(f"Fat: {row['Fat']}g")
        if pd.notna(row.get('Carbohydrates')):
            nutrition_info.append(f"Carbohydrates: {row['Carbohydrates']}g")
        if pd.notna(row.get('Dietary Fiber')):
            nutrition_info.append(f"Fiber: {row['Dietary Fiber']}g")
        if pd.notna(row.get('Vitamin C')):
            nutrition_info.append(f"Vitamin C: {row['Vitamin C']}mg")
        if pd.notna(row.get('Calcium')):
            nutrition_info.append(f"Calcium: {row['Calcium']}mg")
        if pd.notna(row.get('Iron')):
            nutrition_info.append(f"Iron: {row['Iron']}mg")
        
        nutrition_text = ", ".join(nutrition_info)
        
        # Create conversation in Phi-3 format
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": f"What are the nutritional values for {food_name}?"
                },
                {
                    "role": "assistant",
                    "content": f"{food_name} contains: {nutrition_text}"
                }
            ]
        }
        conversations.append(conversation)
    
    logger.info(f"Created {len(conversations)} conversations")
    
    # Convert to Hugging Face Dataset - store both formats
    dataset = Dataset.from_dict({
        "messages": [c["messages"] for c in conversations],
        "text": [f"<|user|>\n{c['messages'][0]['content']}<|end|>\n<|assistant|>\n{c['messages'][1]['content']}<|end|>" for c in conversations]
    })
    
    # Split the dataset
    split_dataset = dataset.train_test_split(test_size=(1 - train_test_split), seed=42)
    train_data = split_dataset["train"]
    test_data = split_dataset["test"]
    
    logger.info(f"Train set size: {len(train_data)}")
    logger.info(f"Test set size: {len(test_data)}")
    
    # Save as JSON Lines format
    train_data.to_json(train_dataset.path, orient="records", lines=True)
    test_data.to_json(test_dataset.path, orient="records", lines=True)
    
    logger.info(f"Saved training data to {train_dataset.path}")
    logger.info(f"Saved test data to {test_dataset.path}")
    
    return {
        "total_samples": len(conversations),
        "train_samples": len(train_data),
        "test_samples": len(test_data),
    }
