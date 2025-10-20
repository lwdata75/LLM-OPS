"""
Script to compile the complete nutrition assistant training pipeline with evaluation.
"""

import os
import sys
from kfp import compiler

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.pipelines.model_training_pipeline import nutrition_assistant_training_pipeline

def compile_pipeline():
    """Compile the pipeline to a YAML file for validation."""
    
    try:
        output_file = "compiled_nutrition_pipeline_with_evaluation.yaml"
        
        print("🔄 Compiling pipeline...")
        compiler.Compiler().compile(
            pipeline_func=nutrition_assistant_training_pipeline,
            package_path=output_file
        )
        
        print(f"✅ Pipeline compiled successfully!")
        print(f"📁 Output file: {output_file}")
        
        # Show file size as validation
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📏 File size: {file_size:,} bytes")
            
        print("\n🎯 Pipeline Summary:")
        print("  Components: 4")
        print("  1. Data Transformation - Preprocess Yoda sentences")
        print("  2. Fine-tuning - Phi-3 with LoRA")  
        print("  3. Inference - Generate predictions")
        print("  4. Evaluation - Compute ragas metrics")
        print("\n🚀 Ready for Vertex AI submission!")
        
    except Exception as e:
        print(f"❌ Pipeline compilation failed: {e}")
        raise

if __name__ == "__main__":
    compile_pipeline()