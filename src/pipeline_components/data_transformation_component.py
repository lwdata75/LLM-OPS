"""
Kubeflow Pipeline component for data transformation.
Converts Yoda sentences dataset to conversational format for Phi-3 fine-tuning.
"""

from kfp.dsl import component, OutputPath
from typing import NamedTuple

@component(
    base_image="python:3.11-slim",
    packages_to_install=[
        "pandas==2.3.3",
        "datasets==4.2.0", 
        "gcsfs==2025.9.0",
        "google-cloud-storage==2.19.0",
        "python-dotenv==1.1.1"
    ]
)
def data_transformation_component(
    input_gcs_path: str,
    output_gcs_bucket: str,
    train_output_path: OutputPath(str),
    test_output_path: OutputPath(str),
    test_size: float = 0.2,
    random_state: int = 42,
    use_extra_translation: bool = True
) -> NamedTuple("DataTransformationOutput", [("train_examples", int), ("test_examples", int)]):
    """
    Data transformation component for Yoda sentences dataset.
    
    Args:
        input_gcs_path (str): GCS path to input CSV file (gs://bucket/path/file.csv)
        output_gcs_bucket (str): GCS bucket name for output files
        train_output_path (OutputPath): Path for training dataset output
        test_output_path (OutputPath): Path for test dataset output
        test_size (float): Proportion of test set (default: 0.2)
        random_state (int): Random seed for reproducibility (default: 42)
        use_extra_translation (bool): Whether to use translation_extra column (default: True)
    
    Returns:
        NamedTuple: Contains train_examples and test_examples counts
    """
    import os
    import pandas as pd
    import datasets
    import logging
    from google.cloud import storage
    import json
    from typing import List, Dict, Any
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Starting data transformation component")
    logger.info(f"Input GCS path: {input_gcs_path}")
    logger.info(f"Output GCS bucket: {output_gcs_bucket}")
    logger.info(f"Test size: {test_size}")
    logger.info(f"Random state: {random_state}")
    logger.info(f"Use extra translation: {use_extra_translation}")
    
    def load_dataset_from_gcs(gcs_path: str) -> pd.DataFrame:
        """Load dataset from GCS."""
        logger.info(f"Loading dataset from {gcs_path}")
        try:
            df = pd.read_csv(gcs_path)
            logger.info(f"Successfully loaded dataset with {len(df)} rows and {len(df.columns)} columns")
            logger.info(f"Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Failed to load dataset from GCS: {str(e)}")
            raise
    
    def format_to_conversational(df: pd.DataFrame, use_extra: bool) -> List[Dict[str, Any]]:
        """Convert to conversational format."""
        logger.info(f"Converting {len(df)} rows to conversational format")
        
        conversations = []
        translation_column = "translation_extra" if use_extra else "translation"
        
        if translation_column not in df.columns:
            logger.warning(f"Column '{translation_column}' not found. Using 'translation' instead.")
            translation_column = "translation"
        
        for _, row in df.iterrows():
            conversation = [
                {"role": "user", "content": row["sentence"]},
                {"role": "assistant", "content": row[translation_column]}
            ]
            conversations.append({"messages": conversation})
        
        logger.info(f"Successfully created {len(conversations)} conversations")
        return conversations
    
    def upload_to_gcs(local_path: str, bucket_name: str, blob_name: str):
        """Upload file to GCS."""
        logger.info(f"Uploading {local_path} to gs://{bucket_name}/{blob_name}")
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            logger.info(f"Successfully uploaded to gs://{bucket_name}/{blob_name}")
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {str(e)}")
            raise
    
    try:
        # Step 1: Load dataset from GCS
        raw_df = load_dataset_from_gcs(input_gcs_path)
        
        # Step 2: Format to conversational format
        conversations = format_to_conversational(raw_df, use_extra_translation)
        
        # Step 3: Convert to Hugging Face Dataset
        logger.info("Converting conversations to Hugging Face Dataset")
        df_conversations = pd.DataFrame(conversations)
        hf_dataset = datasets.Dataset.from_pandas(df_conversations)
        logger.info(f"Created Hugging Face dataset with {len(hf_dataset)} examples")
        
        # Step 4: Split into train/test
        logger.info(f"Splitting dataset with test_size={test_size}, random_state={random_state}")
        split_dataset = hf_dataset.train_test_split(test_size=test_size, seed=random_state)
        train_dataset = split_dataset["train"]
        test_dataset = split_dataset["test"]
        
        logger.info(f"Train set: {len(train_dataset)} examples")
        logger.info(f"Test set: {len(test_dataset)} examples")
        
        # Step 5: Save datasets locally (as JSON)
        logger.info("Saving datasets locally")
        
        # Create temporary local files
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_train_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_test_path = f.name
        
        # Save as JSON
        train_dataset.to_json(temp_train_path)
        test_dataset.to_json(temp_test_path)
        
        # Step 6: Copy to output paths (for Kubeflow)
        import shutil
        shutil.copy2(temp_train_path, train_output_path)
        shutil.copy2(temp_test_path, test_output_path)
        
        logger.info(f"Saved train dataset to: {train_output_path}")
        logger.info(f"Saved test dataset to: {test_output_path}")
        
        # Step 7: Upload to GCS bucket
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d-%H:%M:%S")
        train_gcs_name = f"processed_data/{timestamp}/train_dataset.json"
        test_gcs_name = f"processed_data/{timestamp}/test_dataset.json"
        
        upload_to_gcs(temp_train_path, output_gcs_bucket, train_gcs_name)
        upload_to_gcs(temp_test_path, output_gcs_bucket, test_gcs_name)
        
        # Clean up temporary files
        os.unlink(temp_train_path)
        os.unlink(temp_test_path)
        
        logger.info("✅ Data transformation completed successfully!")
        
        # Return the output tuple
        from collections import namedtuple
        DataTransformationOutput = namedtuple("DataTransformationOutput", ["train_examples", "test_examples"])
        return DataTransformationOutput(train_examples=len(train_dataset), test_examples=len(test_dataset))
        
    except Exception as e:
        logger.error(f"❌ Data transformation failed: {str(e)}")
        raise