"""
Simple script to view processed dataset examples.
"""

import pandas as pd
import ast

def view_examples():
    # Load the processed dataset
    df = pd.read_csv('data/processed/train_dataset.csv')
    
    print(f"📊 Dataset Info:")
    print(f"   Total conversations: {len(df)}")
    print(f"\n🗣️ Sample Conversations:")
    print("=" * 60)
    
    # Show first 3 examples
    for i in range(min(3, len(df))):
        messages = ast.literal_eval(df.iloc[i]['messages'])
        print(f"\nExample {i+1}:")
        print(f"USER: {messages[0]['content']}")
        print(f"YODA: {messages[1]['content']}")
        print("-" * 40)

if __name__ == "__main__":
    view_examples()