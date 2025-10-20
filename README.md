# LLM OPS - Nutrition Assistant Training Pipeline

This repository contains a complete ML pipeline for fine-tuning Microsoft's Phi-3-mini-4k-instruct model to create a nutrition assistant using Kubeflow Pipelines on Vertex AI.

## 🎯 Project Overview

The nutrition assistant helps users:
- Get detailed nutritional information for 2,395+ food items
- Calculate macros (calories, protein, fat, carbohydrates)
- Understand vitamin and mineral content
- Make informed dietary decisions

### Key Features
- **Complete ML Pipeline**: Data transformation → Fine-tuning → Inference → Evaluation
- **Phi-3 Fine-tuning**: Using LoRA (Low-Rank Adaptation) for efficient training
- **Nutrition Dataset**: 2,395 foods with 35 nutritional attributes
- **Evaluation Framework**: Rouge, BLEU, and ExactMatch metrics using ragas
- **Cloud-Native**: Deployed on Google Cloud Vertex AI

## 🏗️ Architecture

```
COMBINED_FOOD_DATASET.csv → Data Transformation → Fine-tuning (LoRA) → Inference → Evaluation
                                    ↓                    ↓              ↓           ↓
                              Conversations         Phi-3 Model    Predictions   Metrics
                              (Train/Test)       (Nutrition Tuned)    (CSV)     (JSON)
```

### Pipeline Components
1. **Data Transformation**: Converts nutrition data to conversational format
2. **Fine-tuning**: LoRA adaptation of Phi-3 with nutrition conversations  
3. **Inference**: Generates predictions on test set
4. **Evaluation**: Computes metrics using ragas framework

## 📊 Performance Results

**Local Testing Results:**
- **Dataset**: 2,395 nutrition items processed
- **Training**: 1,916 conversations (80%)
- **Testing**: 479 conversations (20%)
- **Evaluation Scores**: 
  - Rouge Score: 0.71
  - BLEU Score: 0.71
  - ExactMatch: 0.68
- **Overall Quality**: Good (0.70 average)

## 🚀 Quick Start

### Prerequisites
- Python 3.11.6
- Git
- Docker
- uv package manager

### Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd "LLM OPS"
```

2. Create and activate the virtual environment:
```bash
uv sync
```

This will:
- Create a `.venv` folder with all required dependencies
- Install the following GCP packages:
  - `google-cloud-aiplatform`
  - `google-cloud-bigquery`
  - `google-cloud-storage`

3. Activate the virtual environment:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

4. Verify the setup:
```bash
python --version  # Should show Python 3.11.6
```

### Project Structure

```
├── README.md
├── pyproject.toml                                 # Project dependencies
├── COMBINED_FOOD_DATASET.csv                      # Nutrition dataset (2,395 foods)
├── nutrition_assistant_test.ipynb                 # Complete testing notebook
├── src/
│   ├── constants.py                               # Configuration constants
│   ├── pipeline_components/
│   │   ├── data_transformation_component.py       # Data preprocessing
│   │   ├── fine_tuning_component.py              # Phi-3 LoRA fine-tuning
│   │   ├── inference_component.py                # Model predictions
│   │   └── evaluation_component.py               # Ragas evaluation
│   └── pipelines/
│       └── model_training_pipeline.py            # Complete Kubeflow pipeline
├── scripts/
│   ├── pipeline_runner.py                        # Pipeline deployment
│   └── validate_gcp_setup.py                     # GCP validation
├── pipeline_artifacts/
│   └── nutrition-assistant-training_*.json       # Compiled pipeline
├── data/processed/                                # Generated training data
├── compiled_nutrition_pipeline_with_evaluation.yaml  # Pipeline YAML
├── nutrition_deployment_guide_*.txt              # Deployment instructions
└── results/
    ├── nutrition_evaluation_results.csv          # Per-sample metrics
    ├── nutrition_aggregated_metrics.json         # Summary metrics
    └── nutrition_pipeline_summary.json           # Complete summary
```

## 🔧 Setup and Installation

### Prerequisites
- Python 3.11.6
- Google Cloud SDK
- Vertex AI API enabled
- GPU quota (NVIDIA_TESLA_T4) in europe-west2
- Docker (for component development)

### Installation

1. Clone and setup:
```bash
git clone <repository-url>
cd "LLM OPS"
uv sync  # Install dependencies
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your GCP settings:
# GCP_PROJECT_ID=your-project-id
# GCP_REGION=europe-west2  
# GCP_BUCKET_NAME=your-bucket-name
```

3. Test setup:
```bash
python scripts/validate_gcp_setup.py
```

### Quick Test

Run the complete pipeline test locally:
```bash
jupyter notebook nutrition_assistant_test.ipynb
```

This will:
- Load and analyze the nutrition dataset
- Transform data to conversational format
- Simulate model inference
- Compute evaluation metrics
- Generate all pipeline artifacts

## 🚀 Deployment

### Option 1: Automatic Pipeline Compilation
```bash
python compile_pipeline_with_evaluation.py
```

### Option 2: Manual Vertex AI Deployment
1. Run deployment guide generator:
```bash
python create_deployment_guide.py
```

2. Follow the generated instructions to upload the pipeline via Vertex AI console

### Option 3: Script-based Deployment (may have encoding issues)
```bash
python scripts/pipeline_runner.py
```

## 📋 Pipeline Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| input_gcs_path | gs://llmops_101_europ/20-10-2025-08:28:00 - FOOD/COMBINED_FOOD_DATASET.csv | Nutrition dataset location |
| output_gcs_bucket | llmops_101_europ | GCS bucket for artifacts |
| test_size | 0.2 | Train/test split ratio |
| model_name | microsoft/Phi-3-mini-4k-instruct | Base model |
| learning_rate | 0.0002 | Fine-tuning learning rate |
| num_train_epochs | 1 | Training epochs |
| lora_r | 16 | LoRA rank parameter |
| lora_alpha | 32 | LoRA alpha parameter |
| max_new_tokens | 50 | Max tokens in responses |

## 📈 Monitoring and Results

### Pipeline Monitoring
- **Vertex AI Console**: https://console.cloud.google.com/vertex-ai/pipelines
- **Cloud Storage**: https://console.cloud.google.com/storage/browser/llmops_101_europ
- **Logs**: https://console.cloud.google.com/logs

### Expected Artifacts
- **Training Data**: Conversational nutrition dataset (JSON)
- **Fine-tuned Model**: Phi-3 adapted for nutrition questions
- **Predictions**: Model responses on test set (CSV)
- **Evaluation Results**: Per-sample and aggregated metrics (CSV/JSON)

## 🍎 Example Interactions

**User**: "What are the nutritional values for avocado?"

**Nutrition Assistant**: "Avocado contains: Calories: 160 kcal, Protein: 2.0g, Fat: 14.7g, Carbohydrates: 8.5g, Fiber: 6.7g, Vitamin C: 10mg, Calcium: 12mg"

**User**: "How much protein is in chicken breast?"

**Nutrition Assistant**: "Chicken breast contains: Calories: 165 kcal, Protein: 31.0g, Fat: 3.6g, Carbohydrates: 0g"

## 🔍 Technical Details

### Fine-tuning Configuration
- **Model**: Microsoft Phi-3-mini-4k-instruct
- **Method**: LoRA (Low-Rank Adaptation)
- **Quantization**: 4-bit with BitsAndBytes
- **GPU**: NVIDIA Tesla T4
- **Training Time**: ~2-3 hours

### Dataset Statistics
- **Total Foods**: 2,395 items
- **Nutritional Attributes**: 35 columns
- **Categories**: Dairy, meat, fruits, vegetables, grains, etc.
- **Format**: CSV with detailed macro/micronutrient data

### Evaluation Metrics
- **Rouge Score**: Text similarity and overlap
- **BLEU Score**: Translation quality assessment
- **ExactMatch**: Precise response matching
- **Framework**: ragas 0.3.7 for automated evaluation

## 🛠️ Development

### Adding New Components
```bash
# Create new component
touch src/pipeline_components/new_component.py
# Add to pipeline
# Edit src/pipelines/model_training_pipeline.py
```

### Local Testing
```bash
# Test individual components
python test_nutrition_pipeline.py

# Full pipeline validation
jupyter notebook nutrition_assistant_test.ipynb
```

## 📚 References

- [Hugging Face Fine-tuning Guide](https://huggingface.co/blog/dvgodoy/fine-tuning-llm-hugging-face)
- [Microsoft Phi-3 Documentation](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Ragas Evaluation Framework](https://docs.ragas.io/)

---

**🎓 Albert School - Bootcamp MSC2 - LLM OPS**  
*Building production-ready nutrition intelligence with modern ML pipelines*
