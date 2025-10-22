# 🥗 Nutrition Assistant - Complete MLOps Pipeline# 🥗 Nutrition Assistant - Complete MLOps Pipeline



**Status:** ✅ Production Ready | **Cost:** $0/hour (when undeployed)  **Status:** ✅ Production Ready | **Cost:** $0/hour (when undeployed)

**Built for:** Albert School LLM OPS Bootcamp MSC2  

**Date Completed:** October 21, 2025End-to-end MLOps pipeline for fine-tuning Microsoft Phi-3 on nutrition data using Vertex AI, with production deployment and web interface.



---## 🎯 Project Overview



## 📋 Table of ContentsThis project implements a **complete production ML system** that:

1. **Transforms** nutrition data (2,395 items) into conversational format

1. [Project Overview](#-project-overview)2. **Fine-tunes** Phi-3-mini model with LoRA (Low-Rank Adaptation)

2. [Quick Start](#-quick-start-use-the-chatbot)3. **Deploys** to Vertex AI endpoint with GPU acceleration

3. [Complete Workflow](#-complete-workflow-from-training-to-deployment)4. **Serves** via a beautiful Chainlit chatbot interface

4. [Project Structure](#-project-structure)5. **Manages costs** with easy deploy/undeploy scripts

5. [Configuration](#-configuration)

6. [Cost Management](#-cost-management)## ⚡ Quick Start (Chat with Your Model)

7. [Troubleshooting](#-troubleshooting)

8. [Technical Details](#-technical-details)### Start the Chatbot (3 Commands)

9. [References](#-references)```powershell

python scripts/deploy_to_endpoint.py          # Deploy model (wait 5-10 min)

---python scripts/check_endpoint_status.py        # Verify status = SERVING

python -m chainlit run src/app/main.py -w      # Launch UI at localhost:8000

## 🎯 Project Overview```



This project implements a **complete production MLOps system** for a nutrition chatbot:### Stop Billing (IMPORTANT!)

```powershell

```Ctrl+C                                         # Stop chatbot

End-to-End Pipeline:python scripts/undeploy_model.py               # Stop billing ($0/hour)

┌─────────────────────────────────────────────────────────────────┐```

│ 1. DATA PROCESSING                                              │

│    ├─ 2,395 food items from COMBINED_FOOD_DATASET.csv         │📖 **Full Guide:** See [`HOW_TO_LAUNCH.md`](HOW_TO_LAUNCH.md) or [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)

│    └─ Converted to conversational Q&A format                   │

├─────────────────────────────────────────────────────────────────┤## 🏗️ Architecture

│ 2. MODEL TRAINING (Vertex AI Pipeline)                         │

│    ├─ Fine-tune Phi-3-mini-4k-instruct                        │```

│    ├─ LoRA (Low-Rank Adaptation) - 4-bit quantization         │Complete System:

│    ├─ Training: 3 epochs, batch size 2, lr=2e-4               │├── Training Pipeline (Vertex AI)

│    └─ Resources: Tesla T4 GPU, 16 CPUs, 50GB RAM              ││   ├── Data Transformation → Converts CSV to chat format

├─────────────────────────────────────────────────────────────────┤│   ├── Fine-Tuning → Trains Phi-3 with LoRA on GPU

│ 3. MODEL DEPLOYMENT (Vertex AI Endpoint)                       ││   ├── Inference → Generates predictions

│    ├─ Custom handler for Vertex AI format                     ││   └── Evaluation → Computes Rouge, BLEU metrics

│    ├─ Endpoint with GPU (n1-standard-8 + Tesla T4)           ││

│    └─ Deploy/Undeploy on demand (cost optimization)           │└── Production Deployment

├─────────────────────────────────────────────────────────────────┤    ├── Custom Handler → Processes Vertex AI requests

│ 4. WEB INTERFACE (Chainlit)                                    │    ├── Endpoint → Serves model with Tesla T4 GPU

│    ├─ Beautiful chat interface at localhost:8000              │    └── Chainlit UI → Beautiful chat interface

│    ├─ Google Cloud authentication (ADC)                       │```

│    └─ Real-time responses from fine-tuned model               │

└─────────────────────────────────────────────────────────────────┘## 📋 Prerequisites

```

- Python 3.11.6+

### What You Get- Google Cloud Project with billing enabled

- Vertex AI API enabled

✅ **Training Pipeline** - Automated Vertex AI Kubeflow pipeline  - GPU quota (NVIDIA T4) in your region

✅ **Fine-Tuned Model** - Phi-3 specialized for nutrition questions  - `uv` package manager installed

✅ **Production Deployment** - GPU-accelerated endpoint  

✅ **Web Interface** - User-friendly chatbot  ## 🚀 Quick Start

✅ **Cost Management** - Deploy/undeploy scripts  

✅ **Complete Documentation** - English & French guides  ### 1. Clone and Setup Environment



---```bash

# Clone the repository

## ⚡ Quick Start (Use the Chatbot)git clone <your-repo-url>

cd LLM-OPS

### Prerequisites

# Create virtual environment with uv

```powershelluv sync

# 1. Authenticate with Google Cloud (one time)

gcloud auth application-default login# Activate virtual environment

.venv\Scripts\activate  # Windows

# 2. Verify environment# or

python scripts/check_endpoint_status.pysource .venv/bin/activate  # Linux/Mac

``````



### 🚀 Launcher - Start/Stop Your Chatbot

#### ▶️ Start the Chatbot (3 Steps)

```powershell
# Step 1: Deploy model to endpoint (wait 5-10 minutes)
python scripts/deploy_to_endpoint.py

# Step 2: Verify deployment is complete
python scripts/check_endpoint_status.py
# Look for: "✅ DEPLOYMENT COMPLETE!" and Status: "SERVING"

# Step 3: Launch web interface
python -m chainlit run src/app/main.py -w
# Opens at: http://localhost:8000
```

**🔗 Monitor Your Deployment:**
- **Endpoint Status:** [View in GCP Console](https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/5724492940806455296?project=aerobic-polygon-460910-v9)
- **Pipeline Runs:** [View Training History](https://console.cloud.google.com/vertex-ai/pipelines?project=aerobic-polygon-460910-v9)
- **Storage:** [View GCS Bucket](https://console.cloud.google.com/storage/browser/llmops_101_europ?project=aerobic-polygon-460910-v9)

#### ⏹️ Stop Everything (IMPORTANT - Save Money!)

```powershell
# Step 1: Stop the chatbot interface
# Press Ctrl+C in the terminal running Chainlit

# Step 2: Undeploy model (STOPS BILLING!)
python scripts/undeploy_model.py

# Step 3: Verify model is undeployed
python scripts/check_endpoint_status.py
# Should show: "Status: No models deployed"
```

**💰 Current Cost:** $0/hour when undeployed | ~$0.50-$1.00/hour when deployed

---

### 2. Configure GCP (One-Time Setup)

```bash
# Authenticate with GCP
gcloud auth login
gcloud config set project aerobic-polygon-460910-v9
gcloud auth application-default login

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable compute.googleapis.com
```

### 3. Setup Environment Variables


### Stop Everything (Save Money!)Create a `.env` file in the project root:



```powershell```bash

# 1. Stop chatbot interfaceGCP_PROJECT_ID=aerobic-polygon-460910-v9

Ctrl+C  # in the terminal running ChainlitGCP_REGION=europe-west2

GCP_BUCKET_NAME=llmops_101_europ

# 2. Undeploy model (STOPS BILLING!)```

python scripts/undeploy_model.py

```### 4. Validate GCP Setup



**💡 Pro Tip:** Always run `undeploy_model.py` when done to avoid hourly charges!```bash

python scripts/validate_gcp_setup.py

📖 **Detailed Guide:** See [`docs/guides/HOW_TO_LAUNCH.md`](docs/guides/HOW_TO_LAUNCH.md)```



---### 5. Upload Dataset to GCS



## 🔄 Complete Workflow (From Training to Deployment)```bash

python scripts/upload_dataset.py

### Phase 1: Environment Setup```



```powershell### 6. Run the Pipeline

# 1. Clone and setup

git clone <your-repo-url>```bash

cd "LLM OPS"# Compile and submit to Vertex AI

python scripts/pipeline_runner.py

# 2. Install dependencies

uv sync# Or compile only (for testing)

.venv\Scripts\activate  # Activate virtual environmentpython scripts/pipeline_runner.py --compile-only

```

# 3. Configure GCP

gcloud auth login### 7. Monitor Pipeline

gcloud config set project aerobic-polygon-460910-v9

gcloud auth application-default login```bash

# Check pipeline status

# 4. Create .env filepython scripts/check_pipeline_status.py

# Copy .env.example to .env and fill in values```

```

Or view in GCP Console:

### Phase 2: Train the Modelhttps://console.cloud.google.com/vertex-ai/pipelines



```powershell## 📁 Project Structure

# 1. Validate GCP setup

python scripts/validate_gcp_setup.py```

LLM-OPS/

# 2. Upload dataset to Google Cloud Storage├── 📖 Documentation

python scripts/upload_dataset.py│   ├── HOW_TO_LAUNCH.md              # ⭐ Main guide - start here!

│   ├── QUICK_REFERENCE.md            # Command cheat sheet

# 3. Run training pipeline (takes ~30-45 minutes)│   ├── GUIDE_LANCEMENT_FR.md         # French guide

python scripts/pipeline_runner.py│   ├── PROJECT_COMPLETE.md           # Project summary

│   └── FINAL_STATUS.md               # Current status

# 4. Monitor pipeline progress│

python scripts/check_pipeline_status.py├── 🔧 Configuration

│   ├── .env                          # GCP credentials & endpoint ID

# Or view in GCP Console:│   ├── pyproject.toml                # Python dependencies

# https://console.cloud.google.com/vertex-ai/pipelines│   └── COMBINED_FOOD_DATASET.csv     # Training data (2,395 items)

```│

├── 🚀 Deployment Scripts

**What Happens During Training:**│   ├── scripts/deploy_to_endpoint.py        # Deploy model (start billing)

│   ├── scripts/undeploy_model.py            # Stop billing

1. **Data Transformation** - Converts CSV to chat format│   ├── scripts/check_endpoint_status.py     # Check deployment

2. **Fine-Tuning** - Trains Phi-3 with LoRA on GPU│   ├── scripts/delete_endpoint.py           # Delete endpoint

3. **Inference** - Generates predictions on test set│   └── scripts/register_model_with_custom_handler.py

4. **Evaluation** - Computes Rouge and BLEU scores│

├── 🎓 Training Scripts

**Training Output:** Model saved to `gs://llmops_101_europ/pipeline_root/.../fine_tuned_model`│   ├── scripts/validate_gcp_setup.py        # Validate GCP

│   ├── scripts/upload_dataset.py            # Upload data

### Phase 3: Deploy to Production│   ├── scripts/pipeline_runner.py           # Run training pipeline

│   └── scripts/check_pipeline_status.py     # Monitor training

```powershell│

# 1. Register model to Vertex AI├── 🧠 Source Code

python scripts/register_model_with_custom_handler.py \│   ├── src/handler.py                       # Custom endpoint handler

    --model-uri "gs://llmops_101_europ/pipeline_root/.../fine_tuned_model" \│   ├── src/app/main.py                      # Chainlit chatbot UI

    --model-name "nutrition-assistant-phi3"│   ├── src/constants.py                     # Configuration

│   ├── src/pipeline_components/             # Pipeline components

# 2. Deploy to endpoint (creates endpoint + deploys model)│   │   ├── data_transformation_component.py

python scripts/deploy_to_endpoint.py│   │   ├── fine_tuning_component.py

│   │   ├── inference_component.py

# 3. Wait for deployment (5-10 minutes)│   │   └── evaluation_component.py

python scripts/check_endpoint_status.py│   └── src/pipelines/

```│       └── model_training_pipeline.py

│

### Phase 4: Use the Chatbot└── 📊 Data & Artifacts

    └── data/processed/                      # Processed data

```powershell```

# Launch web interface

python -m chainlit run src/app/main.py -w## 🔧 Configuration



# Open browser to: http://localhost:8000### Training Hyperparameters

# Ask questions like:

# - "What are the health benefits of spinach?"Configured in `src/constants.py`:

# - "List high-protein foods"

# - "Which foods are rich in vitamin C?"```python

```TRAINING_CONFIG = {

    "max_seq_length": 512,

### Phase 5: Clean Up    "num_train_epochs": 3,

    "per_device_train_batch_size": 2,

```powershell    "learning_rate": 2e-4,

# Stop chatbot    # ... more parameters

Ctrl+C}

```

# Undeploy model (IMPORTANT - stops billing!)

python scripts/undeploy_model.py### LoRA Configuration



# Optional: Delete endpoint completely```python

python scripts/delete_endpoint.pyLORA_CONFIG = {

```    "r": 16,

    "lora_alpha": 32,

---    "lora_dropout": 0.05,

    "target_modules": ["q_proj", "k_proj", "v_proj", ...],

## 📁 Project Structure}

```

```

LLM OPS/## 📊 Dataset

│

├── 📖 README.md                          # ⭐ Main documentation (you are here)- **Source**: COMBINED_FOOD_DATASET.csv

├── 📋 .env.example                       # Environment template- **Size**: 2,395 food items

├── 📊 COMBINED_FOOD_DATASET.csv          # Training data (2,395 items)- **Format**: CSV with nutritional information

├── ⚙️  pyproject.toml                    # Python dependencies- **Output**: Conversational Q&A format for Phi-3

│

├── 📚 docs/                              # Documentation### Example Conversation

│   ├── guides/                           # User guides

│   │   ├── HOW_TO_LAUNCH.md             # Complete launch guide```json

│   │   ├── GUIDE_LANCEMENT_FR.md        # French guide{

│   │   └── QUICK_REFERENCE.md           # Command cheat sheet  "user": "What are the nutritional values for olive oil?",

│   ├── references/                       # Technical references  "assistant": "olive oil contains: Calories: 119 kcal, Fat: 13.5g"

│   │   ├── PROJECT_COMPLETE.md          # Project summary}

│   │   ├── FINAL_STATUS.md              # Current status```

│   │   ├── SESSION4_DEPLOYMENT_GUIDE.md

│   │   ├── SESSION4_IMPLEMENTATION_SUMMARY.md## 🎛️ Pipeline Components

│   │   └── session[1-4]_practice.md     # Practice exercises

│   └── archive/                          # Old/deprecated docs### 1. Data Transformation

│- Reads CSV from GCS

├── 🚀 scripts/                           # Utility scripts- Converts to chat format

│   ├── Training Scripts:- Splits into train/test sets

│   │   ├── validate_gcp_setup.py        # Validate GCP connection- Saves as JSON Lines

│   │   ├── upload_dataset.py            # Upload data to GCS

│   │   ├── pipeline_runner.py           # Run training pipeline### 2. Fine-Tuning

│   │   └── check_pipeline_status.py     # Monitor training- Loads Phi-3-mini-4k-instruct

│   │- Applies 4-bit quantization

│   ├── Deployment Scripts:- Trains with LoRA adapters

│   │   ├── register_model_with_custom_handler.py  # Register model- Saves model to GCS

│   │   ├── deploy_to_endpoint.py        # Deploy model (starts billing)- **Resources**: T4 GPU, 16 CPU, 50GB RAM

│   │   ├── undeploy_model.py            # Undeploy (stops billing)

│   │   ├── delete_endpoint.py           # Delete endpoint### 3. Inference

│   │   └── check_endpoint_status.py     # Check deployment status- Loads fine-tuned model

│   │- Generates predictions

│   └── Utility Scripts:- Extracts responses

│       ├── find_model_uri.py            # Find model URI in GCS- Saves as CSV

│       ├── get_console_urls.py          # Generate GCP console URLs- **Resources**: T4 GPU, 8 CPU, 32GB RAM

│       └── ...other utilities

│### 4. Evaluation

├── 🧠 src/                               # Source code- Computes RAGAS metrics

│   ├── handler.py                        # Custom Vertex AI handler- RougeScore, BleuScore

│   ├── constants.py                      # Configuration constants- Per-sample and aggregated results

│   ├── data_processing.py                # Data utilities- **Resources**: 4 CPU, 8GB RAM

│   │

│   ├── app/                              # Chainlit web application## 📈 Monitoring & Results

│   │   └── main.py                       # Chatbot interface

│   │### View Pipeline in GCP Console

│   ├── pipelines/                        # Pipeline definitions

│   │   └── model_training_pipeline.py    # Main training pipeline```

│   │https://console.cloud.google.com/vertex-ai/pipelines?project=aerobic-polygon-460910-v9

│   └── pipeline_components/              # Pipeline components```

│       ├── data_transformation_component.py

│       ├── fine_tuning_component.py### Check Artifacts

│       ├── inference_component.py

│       └── evaluation_component.pyAll artifacts are stored in GCS:

│```

├── 📊 data/                              # Processed datags://llmops_101_europ/

│   └── processed/├── pipeline_root/          # Pipeline execution artifacts

│       └── sample_nutrition_conversations.json├── data/                   # Processed datasets

│└── models/                 # Fine-tuned models

├── 🧪 tests/                             # Test scripts```

│   ├── test_data_processing.py

│   ├── test_nutrition_model.py### Metrics

│   ├── verify_pipeline.py

│   └── view_examples.pyPipeline outputs:

│- Training loss curves

├── 📦 compiled_pipelines/                # Compiled pipeline YAMLs- Evaluation metrics (Rouge, BLEU)

│   ├── compiled_nutrition_pipeline.yaml- Per-sample predictions

│   └── ...pipeline compilation scripts- Model checkpoints

│

├── 📈 outputs/                           # Pipeline outputs & artifacts## 🛠️ Troubleshooting

│   ├── inference_predictions.csv

│   ├── nutrition_evaluation_results.csv### GPU Quota Error

│   └── pipeline_artifacts/

│If you get a quota error:

└── 🔧 .chainlit/                         # Chainlit configuration1. Go to GCP Console → IAM & Admin → Quotas

    ├── config.toml2. Filter: "Vertex AI", "europe-west2", "NVIDIA T4"

    └── translations/                     # Multi-language support3. Request quota increase to at least 1

```

### Authentication Error

---

```bash

## ⚙️ Configurationgcloud auth application-default login

```

### Environment Variables (.env)

### Pipeline Fails at Fine-Tuning

```bash

# GCP Project ConfigurationCheck:

GCP_PROJECT_ID=aerobic-polygon-460910-v9- GPU quota is approved

GCP_PROJECT_NUMBER=432566588992- Region matches (europe-west2)

GCP_REGION=europe-west2- Dataset is uploaded to GCS

GCP_BUCKET_NAME=llmops_101_europ- Bucket permissions are correct



# Deployment Configuration (set after deployment)## 🔄 Iterating on the Pipeline

GCP_ENDPOINT_ID=5724492940806455296

```### Update hyperparameters:

Edit `src/constants.py` and re-run:

### Training Configuration (`src/constants.py`)```bash

python scripts/pipeline_runner.py

```python```

# Model

BASE_MODEL = "microsoft/Phi-3-mini-4k-instruct"### Test changes locally:

```bash

# Training Hyperparameterspython scripts/pipeline_runner.py --compile-only

TRAINING_CONFIG = {```

    "max_seq_length": 512,

    "num_train_epochs": 3,### Enable caching:

    "per_device_train_batch_size": 2,```bash

    "gradient_accumulation_steps": 4,python scripts/pipeline_runner.py --enable-caching

    "learning_rate": 2e-4,```

    "weight_decay": 0.01,

    "warmup_ratio": 0.1,## 📚 Resources

}

- [Vertex AI Pipelines Documentation](https://cloud.google.com/vertex-ai/docs/pipelines)

# LoRA Configuration- [Phi-3 Model Card](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

LORA_CONFIG = {- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)

    "r": 16,- [LoRA Paper](https://arxiv.org/abs/2106.09685)

    "lora_alpha": 32,

    "lora_dropout": 0.05,## 📝 License

    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", 

                      "gate_proj", "up_proj", "down_proj"],This project is for educational purposes as part of the Albert School LLM OPS Bootcamp.

}

```## � Cost Management



---| Status | Cost/Hour | When |

|--------|-----------|------|

## 💰 Cost Management| ✅ Model Undeployed | **$0.00** | Default (safe) |

| ⚠️ Model Deployed | **$0.50-$1.00** | While testing |

### Current Costs (Model Undeployed)| 💾 Storage (GCS) | **~$0.001** | Always (minimal) |



| Component | Status | Cost/Hour | Cost/Month |**💡 Best Practice:** Always run `python scripts/undeploy_model.py` after testing!

|-----------|--------|-----------|------------|

| **Endpoint (empty)** | ✅ Active | $0.00 | $0.00 |## 📚 Key Documentation

| **GCS Storage** | ✅ Active | ~$0.001 | ~$0.72 |

| **Model Deployment** | ⚪ Undeployed | $0.00 | $0.00 |- **[HOW_TO_LAUNCH.md](HOW_TO_LAUNCH.md)** - Complete launch guide with troubleshooting

| **Total** | | **$0.001/hour** | **~$0.72/month** |- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page command reference

- **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** - Full project summary

### Costs When Deployed- **[FINAL_STATUS.md](FINAL_STATUS.md)** - Current deployment status



| Component | Machine Type | Cost/Hour | Cost/Day (8hrs) |## 🎓 What's Included

|-----------|--------------|-----------|-----------------|

| **Endpoint + Model** | n1-standard-8 + Tesla T4 | $0.50-$1.00 | $4.00-$8.00 |✅ **Training Pipeline** - Vertex AI Kubeflow pipeline with 4 components  

✅ **Model Deployment** - Production endpoint with GPU (Tesla T4)  

### Cost Optimization Tips✅ **Web Interface** - Chainlit chatbot for easy interaction  

✅ **Cost Management** - Scripts to deploy/undeploy on demand  

1. **Always undeploy after testing**✅ **Complete Docs** - English & French guides, troubleshooting  

   ```powershell✅ **Authentication** - Google Cloud Application Default Credentials  

   python scripts/undeploy_model.py

   ```## 🙋 Support



2. **Check deployment status before leaving**### Quick Checks

   ```powershell```powershell

   python scripts/check_endpoint_status.pypython scripts/check_endpoint_status.py      # Check deployment

   ```python scripts/check_pipeline_status.py      # Check training

```

3. **Delete endpoint if not using for weeks**

   ```powershell### Troubleshooting

   python scripts/delete_endpoint.pySee **[HOW_TO_LAUNCH.md](HOW_TO_LAUNCH.md)** → Section "🔧 Troubleshooting"

   ```

### GCP Console

---- **Endpoints:** https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/5724492940806455296?project=aerobic-polygon-460910-v9

- **Pipelines:** https://console.cloud.google.com/vertex-ai/pipelines?project=aerobic-polygon-460910-v9

## 🔧 Troubleshooting

---

### Authentication Issues

## 🎉 Project Status

**Problem:** "Error getting access token"

**✅ COMPLETE & PRODUCTION READY**

```powershell

# Solution: Re-authenticate- Model trained on 2,395 nutrition items

gcloud auth application-default login- Deployed to Vertex AI (currently undeployed to save costs)

```- Chatbot interface ready to launch

- All documentation complete

### Model Not Responding- Cost management implemented



**Problem:** Chatbot shows errors**Current Billing:** $0/hour (model undeployed) 💰



```powershell---

# 1. Check endpoint status

python scripts/check_endpoint_status.py**Made with ❤️ for Albert School - LLM OPS Bootcamp MSC2**  

**Completed:** October 21, 2025

# 2. Verify model is deployed (Status: "SERVING")

# 3. If not deployed, redeploy**🥗 Your AI Nutrition Assistant is Ready! Launch it with [`HOW_TO_LAUNCH.md`](HOW_TO_LAUNCH.md)**

python scripts/deploy_to_endpoint.py
```

### Chainlit Won't Start

**Problem:** "chainlit command not found"

```powershell
# Solution: Use python -m
python -m chainlit run src/app/main.py -w

# Or install packages
pip install chainlit google-auth
```

📖 **More Help:** See [`docs/guides/HOW_TO_LAUNCH.md`](docs/guides/HOW_TO_LAUNCH.md) → Troubleshooting section

---

## 🔬 Technical Details

### Model Architecture

- **Base Model:** Microsoft Phi-3-mini-4k-instruct (3.8B parameters)
- **Fine-Tuning:** LoRA (Low-Rank Adaptation)
- **Quantization:** 4-bit NF4 with BitsAndBytes
- **Context Length:** 4,096 tokens
- **Trainable Parameters:** ~0.2% of total

### Training Details

- **Dataset:** 2,395 nutrition conversations
- **Training Time:** ~30-45 minutes on Tesla T4
- **GPU Memory:** ~15GB (with 4-bit quantization)
- **Optimizer:** AdamW with warmup

### Deployment Details

- **Container:** Pre-built HuggingFace Inference (PyTorch 2.4, CUDA 12.1)
- **Machine Type:** n1-standard-8 (8 vCPUs, 30GB RAM)
- **Accelerator:** NVIDIA Tesla T4 (16GB VRAM)
- **Replicas:** 1 (auto-scaling ready)

---

## 📚 References

### Documentation

- **User Guides:**
  - [`docs/guides/HOW_TO_LAUNCH.md`](docs/guides/HOW_TO_LAUNCH.md) - Complete launch guide
  - [`docs/guides/QUICK_REFERENCE.md`](docs/guides/QUICK_REFERENCE.md) - Command cheat sheet
  - [`docs/guides/GUIDE_LANCEMENT_FR.md`](docs/guides/GUIDE_LANCEMENT_FR.md) - Guide en français

- **Technical References:**
  - [`docs/references/PROJECT_COMPLETE.md`](docs/references/PROJECT_COMPLETE.md) - Full summary
  - [`docs/references/FINAL_STATUS.md`](docs/references/FINAL_STATUS.md) - Current status

### GCP Console Links

- **Endpoints:** [Your Endpoint](https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/5724492940806455296?project=aerobic-polygon-460910-v9)
- **Pipelines:** [Training Pipelines](https://console.cloud.google.com/vertex-ai/pipelines?project=aerobic-polygon-460910-v9)
- **Storage:** [GCS Bucket](https://console.cloud.google.com/storage/browser/llmops_101_europ?project=aerobic-polygon-460910-v9)

### Quick Commands Reference

```powershell
# Training
python scripts/validate_gcp_setup.py         # Validate setup
python scripts/upload_dataset.py             # Upload data
python scripts/pipeline_runner.py            # Train model
python scripts/check_pipeline_status.py      # Check training

# Deployment
python scripts/deploy_to_endpoint.py         # Deploy (start billing)
python scripts/check_endpoint_status.py      # Check status
python scripts/undeploy_model.py             # Undeploy (stop billing)

# Usage
python -m chainlit run src/app/main.py -w    # Launch chatbot

# Authentication
gcloud auth application-default login        # Re-authenticate
```

---

## 🎉 Project Status

**✅ COMPLETE & PRODUCTION READY**

- ✅ Model trained on 2,395 nutrition items
- ✅ Deployed to Vertex AI (currently undeployed)
- ✅ Chatbot interface ready
- ✅ Documentation complete
- ✅ Cost management implemented

**Current Billing:** $0/hour (model undeployed) 💰

---

## 👥 Project Info

- **Built for:** Albert School LLM OPS Bootcamp MSC2
- **Date Completed:** October 21, 2025
- **GCP Project:** aerobic-polygon-460910-v9
- **Region:** europe-west2
- **Endpoint ID:** 5724492940806455296
- **Model ID:** 3561348948692041728

---

**Made with ❤️ for Albert School**

**🥗 Your AI Nutrition Assistant is Ready!**

Start with: [`docs/guides/HOW_TO_LAUNCH.md`](docs/guides/HOW_TO_LAUNCH.md)
