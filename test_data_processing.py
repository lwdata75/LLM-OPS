"""
Unit tests for data processing module.
"""

import unittest
import tempfile
import os
import pandas as pd
import json
from unittest.mock import patch
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.data_processing import (
    format_to_conversational,
    convert_to_hf_dataset,
    split_dataset,
    save_datasets_locally
)

class TestDataProcessing(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'sentence': [
                'The quick brown fox jumps.',
                'It is a sunny day today.'
            ],
            'translation': [
                'Jumps, the quick brown fox does.',
                'A sunny day today, it is.'
            ],
            'translation_extra': [
                'Jumps, the quick brown fox does. Yes, hrrrm.',
                'A sunny day today, it is. Hmm.'
            ]
        })
    
    def test_format_to_conversational(self):
        """Test conversion to conversational format."""
        conversations = format_to_conversational(self.sample_data, use_extra_translation=True)
        
        # Check the structure
        self.assertEqual(len(conversations), 2)
        self.assertIn('messages', conversations[0])
        
        # Check the first conversation
        first_conversation = conversations[0]['messages']
        self.assertEqual(len(first_conversation), 2)
        self.assertEqual(first_conversation[0]['role'], 'user')
        self.assertEqual(first_conversation[1]['role'], 'assistant')
        self.assertEqual(first_conversation[0]['content'], 'The quick brown fox jumps.')
        self.assertEqual(first_conversation[1]['content'], 'Jumps, the quick brown fox does. Yes, hrrrm.')
    
    def test_format_to_conversational_basic_translation(self):
        """Test conversion using basic translation (not extra)."""
        conversations = format_to_conversational(self.sample_data, use_extra_translation=False)
        
        first_conversation = conversations[0]['messages']
        self.assertEqual(first_conversation[1]['content'], 'Jumps, the quick brown fox does.')
    
    def test_convert_to_hf_dataset(self):
        """Test conversion to Hugging Face dataset."""
        conversations = format_to_conversational(self.sample_data)
        hf_dataset = convert_to_hf_dataset(conversations)
        
        self.assertEqual(len(hf_dataset), 2)
        self.assertIn('messages', hf_dataset.column_names)
    
    def test_split_dataset(self):
        """Test dataset splitting."""
        conversations = format_to_conversational(self.sample_data)
        hf_dataset = convert_to_hf_dataset(conversations)
        
        # For such a small dataset, let's use a larger test size
        train_dataset, test_dataset = split_dataset(hf_dataset, test_size=0.5, random_state=42)
        
        self.assertEqual(len(train_dataset) + len(test_dataset), len(hf_dataset))
        self.assertGreaterEqual(len(train_dataset), 1)
        self.assertGreaterEqual(len(test_dataset), 1)
    
    def test_save_datasets_locally(self):
        """Test saving datasets to local files."""
        conversations = format_to_conversational(self.sample_data)
        hf_dataset = convert_to_hf_dataset(conversations)
        train_dataset, test_dataset = split_dataset(hf_dataset, test_size=0.5, random_state=42)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            train_path, test_path = save_datasets_locally(train_dataset, test_dataset, temp_dir)
            
            # Check files exist
            self.assertTrue(os.path.exists(train_path))
            self.assertTrue(os.path.exists(test_path))
            
            # Check file contents
            with open(train_path, 'r') as f:
                train_data = [json.loads(line) for line in f]
            
            with open(test_path, 'r') as f:
                test_data = [json.loads(line) for line in f]
            
            self.assertGreater(len(train_data), 0)
            self.assertGreater(len(test_data), 0)
            
            # Check data structure
            self.assertIn('messages', train_data[0])
            self.assertEqual(len(train_data[0]['messages']), 2)
            self.assertEqual(train_data[0]['messages'][0]['role'], 'user')
            self.assertEqual(train_data[0]['messages'][1]['role'], 'assistant')

if __name__ == '__main__':
    unittest.main()