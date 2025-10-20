"""
Script de validation finale pour le projet Nutrition Assistant
"""

import os
import json
import pandas as pd
from datetime import datetime

def validate_project_structure():
    """Valider que tous les fichiers nécessaires sont présents."""
    print("🔍 Validating project structure...")
    
    required_files = [
        "COMBINED_FOOD_DATASET.csv",
        "src/constants.py",
        "src/pipeline_components/data_transformation_component.py",
        "src/pipeline_components/fine_tuning_component.py", 
        "src/pipeline_components/inference_component.py",
        "src/pipeline_components/evaluation_component.py",
        "src/pipelines/model_training_pipeline.py",
        "scripts/pipeline_runner.py",
        "compile_pipeline_with_evaluation.py",
        "nutrition_assistant_test.ipynb",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def validate_dataset():
    """Valider le dataset nutrition."""
    print("\n🍎 Validating nutrition dataset...")
    
    try:
        df = pd.read_csv("COMBINED_FOOD_DATASET.csv")
        
        print(f"   - Rows: {len(df):,}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - Size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Vérifier les colonnes importantes
        required_columns = ['food', 'Caloric Value', 'Protein', 'Fat', 'Carbohydrates']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            return False
        else:
            print("✅ Dataset structure valid")
            return True
            
    except Exception as e:
        print(f"❌ Dataset validation failed: {e}")
        return False

def validate_pipeline_artifacts():
    """Valider les artifacts de pipeline."""
    print("\n🔧 Validating pipeline artifacts...")
    
    # Vérifier le dossier pipeline_artifacts
    if not os.path.exists("pipeline_artifacts"):
        print("❌ pipeline_artifacts directory missing")
        return False
    
    # Chercher les fichiers de pipeline
    pipeline_files = [f for f in os.listdir("pipeline_artifacts") 
                     if f.startswith("nutrition-assistant-training") and f.endswith(".json")]
    
    if not pipeline_files:
        print("❌ No compiled pipeline files found")
        return False
    
    latest_pipeline = sorted(pipeline_files)[-1]
    pipeline_path = f"pipeline_artifacts/{latest_pipeline}"
    file_size = os.path.getsize(pipeline_path)
    
    print(f"✅ Pipeline compiled: {latest_pipeline}")
    print(f"   - Size: {file_size:,} bytes")
    
    # Vérifier le YAML
    yaml_files = [f for f in os.listdir(".") if f.startswith("compiled_nutrition_pipeline") and f.endswith(".yaml")]
    if yaml_files:
        yaml_file = yaml_files[0]
        yaml_size = os.path.getsize(yaml_file)
        print(f"✅ YAML pipeline: {yaml_file} ({yaml_size:,} bytes)")
    
    return True

def validate_generated_files():
    """Valider les fichiers générés lors des tests."""
    print("\n📊 Validating generated test files...")
    
    test_files = [
        "nutrition_evaluation_results.csv",
        "nutrition_aggregated_metrics.json", 
        "nutrition_pipeline_summary.json",
        "inference_predictions.csv"
    ]
    
    valid_files = []
    for file_path in test_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {file_size:,} bytes")
            valid_files.append(file_path)
        else:
            print(f"⚠️  {file_path}: Not found (will be generated during pipeline run)")
    
    return len(valid_files) > 0

def validate_configuration():
    """Valider la configuration GCP."""
    print("\n⚙️  Validating configuration...")
    
    try:
        from src.constants import validate_constants, GCP_PROJECT_ID, GCP_BUCKET_NAME, RAW_DATA_GCS_PATH
        
        validate_constants()
        print(f"✅ GCP Project: {GCP_PROJECT_ID}")
        print(f"✅ GCS Bucket: {GCP_BUCKET_NAME}")
        print(f"✅ Data Path: {RAW_DATA_GCS_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def create_validation_report():
    """Créer un rapport de validation."""
    print("\n📋 Creating validation report...")
    
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "project_name": "nutrition-assistant-training-pipeline",
        "validations": {
            "project_structure": validate_project_structure(),
            "dataset": validate_dataset(),
            "pipeline_artifacts": validate_pipeline_artifacts(),
            "generated_files": validate_generated_files(),
            "configuration": validate_configuration()
        }
    }
    
    # Informations supplémentaires
    if os.path.exists("COMBINED_FOOD_DATASET.csv"):
        df = pd.read_csv("COMBINED_FOOD_DATASET.csv")
        report["dataset_info"] = {
            "total_foods": len(df),
            "columns": len(df.columns),
            "size_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
    
    if os.path.exists("nutrition_pipeline_summary.json"):
        with open("nutrition_pipeline_summary.json", "r") as f:
            summary = json.load(f)
            report["test_results"] = summary.get("evaluation_info", {})
    
    # Sauvegarder le rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"nutrition_validation_report_{timestamp}.json"
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Résumé
    all_valid = all(report["validations"].values())
    status = "✅ READY" if all_valid else "⚠️  NEEDS ATTENTION"
    
    print(f"\n{'='*60}")
    print(f"🍎 NUTRITION ASSISTANT PIPELINE VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Status: {status}")
    print(f"Report saved: {report_path}")
    
    for check, result in report["validations"].items():
        icon = "✅" if result else "❌"
        print(f"{icon} {check.replace('_', ' ').title()}: {'PASS' if result else 'FAIL'}")
    
    if all_valid:
        print(f"\n🚀 Pipeline ready for deployment!")
        print(f"   - Use: python create_deployment_guide.py")
        print(f"   - Or manually upload: pipeline_artifacts/nutrition-assistant-training_*.json")
        print(f"   - Vertex AI Console: https://console.cloud.google.com/vertex-ai/pipelines")
    else:
        print(f"\n🔧 Please address the failed validations before deployment.")
    
    return report_path, all_valid

if __name__ == "__main__":
    print("🍎 NUTRITION ASSISTANT PIPELINE - Final Validation")
    print("="*60)
    
    report_path, all_valid = create_validation_report()
    
    if all_valid:
        print(f"\n🎉 All validations passed!")
        print(f"📁 Validation report: {report_path}")
        print(f"🚀 Ready to deploy the nutrition assistant pipeline!")
    else:
        print(f"\n⚠️  Some validations failed. Please check the details above.")
        exit(1)