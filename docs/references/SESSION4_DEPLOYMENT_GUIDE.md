# 🚀 Session 4 Deployment Guide - Nutrition Assistant

## ✅ What's Been Completed

### 1. ✅ Custom EndpointHandler Created
- **File**: `src/handler.py`
- **Features**:
  - Loads fine-tuned Phi-3 model with LoRA adapters
  - Handles Vertex AI prediction format (instances/parameters)
  - Applies chat template for proper conversation formatting
  - Extracts clean assistant responses
  - Supports GPU and CPU inference

### 2. ✅ Model Registration Script Created
- **File**: `scripts/register_model_with_custom_handler.py`
- **Features**:
  - Uploads handler.py to GCS model artifacts
  - Registers model to Vertex AI Model Registry
  - Uses pre-built HuggingFace container
  - Supports model versioning

### 3. ✅ Model Successfully Registered to Vertex AI
- **Model Name**: nutrition-assistant-phi3
- **Model ID**: 3561348948692041728
- **Version**: 1
- **Artifact URI**: `gs://llmops_101_europ/pipeline_root/432566588992/nutrition-assistant-training-pipeline-20251021140422/fine-tuning-component_-346527857045929984/fine_tuned_model`
- **Console Link**: https://console.cloud.google.com/vertex-ai/models/3561348948692041728?project=aerobic-polygon-460910-v9

### 4. ✅ Chainlit Web App Created
- **File**: `src/app/main.py`
- **Features**:
  - Chat interface for nutrition questions
  - Authenticates with GCP using gcloud token
  - Sends requests to Vertex AI endpoint
  - Extracts and displays assistant responses
  - Includes starter prompts for common questions

---

## 📋 Next Steps: Deploy Model to Endpoint

### Step 1: Deploy to Vertex AI Endpoint (15-30 minutes)

1. **Open the Model in Console**:
   - Go to: https://console.cloud.google.com/vertex-ai/models/3561348948692041728?project=aerobic-polygon-460910-v9
   - Or navigate to: Vertex AI → Model Registry → nutrition-assistant-phi3

2. **Start Deployment**:
   - Click the **three dots (⋮)** on the right side of the model
   - Select **"Deploy to endpoint"**

3. **Create New Endpoint**:
   - Click **"Create new endpoint"**
   - **Endpoint name**: `nutrition-assistant-endpoint`
   - **Region**: `europe-west2` (must match your model)
   - Click **"Continue"**

4. **Configure Deployment**:
   - **Model settings**:
     - Traffic split: 100% (default)
     - Click **"Continue"**
   
   - **Compute and scaling**:
     - **Machine type**: `n1-standard-8` (8 vCPUs, 30 GB memory)
     - **Accelerator**: Select **NVIDIA Tesla T4**
     - **Accelerator count**: `1`
     - **Minimum number of nodes**: `1`
     - **Maximum number of nodes**: `1` (no autoscaling for testing)
     - Click **"Continue"**
   
   - **Model monitoring** (optional):
     - Skip for now (click **"Continue"**)
   
   - **Explainability** (optional):
     - Skip (click **"Deploy"**)

5. **Wait for Deployment**:
   - The deployment will take **15-30 minutes**
   - You can monitor progress in the Endpoints page
   - Check logs: Click **⋮** → **"View logs"** to see deployment progress

---

### Step 2: Configure Environment Variables

Once deployment is complete:

1. **Get the Endpoint ID**:
   - Go to: Vertex AI → Endpoints
   - Click on `nutrition-assistant-endpoint`
   - Copy the **Endpoint ID** (numbers at the end of the Resource name)

2. **Update .env file**:
   ```bash
   # Add these lines to your .env file
   GCP_PROJECT_NUMBER=432566588992
   GCP_ENDPOINT_ID=your-endpoint-id-here  # Replace with actual ID
   ```

---

### Step 3: Test the Endpoint with curl

Once deployment is complete and .env is updated:

#### PowerShell Command:
```powershell
$ACCESS_TOKEN = gcloud auth print-access-token
$PROJECT_NUMBER = "432566588992"
$REGION = "europe-west2"
$ENDPOINT_ID = "your-endpoint-id-here"  # Replace with your actual endpoint ID

curl -X POST `
  -H "Authorization: Bearer $ACCESS_TOKEN" `
  -H "Content-Type: application/json" `
  "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_NUMBER}/locations/${REGION}/endpoints/${ENDPOINT_ID}:predict" `
  -d "@sample_input.json"
```

**Expected Response**:
```json
{
  "predictions": [
    {
      "generated_text": "Spinach is rich in vitamins A, C, and K, and minerals like iron and calcium..."
    }
  ]
}
```

---

### Step 4: Install Dependencies and Run Chainlit App

1. **Install Chainlit**:
   ```powershell
   pip install chainlit requests
   ```

2. **Run the Web App**:
   ```powershell
   chainlit run src/app/main.py -w
   ```

3. **Open Browser**:
   - The app will open at: http://localhost:8000
   - Try the starter prompts or ask your own nutrition questions!

---

## 📁 Files Created

```
src/
├── handler.py                                  # ✅ Custom EndpointHandler
└── app/
    └── main.py                                 # ✅ Chainlit web application

scripts/
├── register_model_with_custom_handler.py       # ✅ Model registration script
├── get_model_artifact_uri.py                   # Helper: Get pipeline outputs
├── find_model_uri.py                           # Helper: Find model in GCS
└── get_task_details.py                         # Helper: Get task details

sample_input.json                               # ✅ Sample API request
.env.example                                    # ✅ Updated with new variables
```

---

## 🧪 Testing Workflow

### Test 1: Local Handler Testing (Optional)

Download the model locally and test the handler:

```powershell
# Download model from GCS
gsutil -m cp -r gs://llmops_101_europ/pipeline_root/432566588992/nutrition-assistant-training-pipeline-20251021140422/fine-tuning-component_-346527857045929984/fine_tuned_model ./local_model

# Set environment variable
$env:LOCAL_MODEL_DIR = "./local_model"

# Run handler test
python src/handler.py
```

### Test 2: Endpoint Testing

Use curl command from Step 3 above.

### Test 3: Web App Testing

1. Run Chainlit app (Step 4 above)
2. Try these questions:
   - "What are the nutritional benefits of spinach?"
   - "What are some high-protein foods?"
   - "Which foods are rich in vitamin C?"
   - "Can you suggest some healthy snack options?"

---

## 🎯 Model Information

- **Base Model**: microsoft/Phi-3-mini-4k-instruct
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **Training Dataset**: 2,395 nutrition conversations
- **Training Config**:
  - Epochs: 3
  - Batch size: 2 per device
  - Learning rate: 2e-4
  - LoRA rank: 16
  - LoRA alpha: 32
- **Quantization**: 4-bit (NF4) with BitsAndBytes

---

## ⚠️ Important Reminders

### Cost Management
- **Endpoint costs money while running!** (~$0.50-$1.00 per hour for T4 GPU)
- **Delete the endpoint when done**:
  1. Go to Vertex AI → Endpoints
  2. Select your endpoint
  3. Click **"Undeploy model"** first
  4. Then click **"Delete endpoint"**

### Quotas
- Make sure you have T4 GPU quota in `europe-west2`
- Check: IAM & Admin → Quotas → Filter "NVIDIA T4"

---

## 🔧 Troubleshooting

### Issue: Deployment fails with "Quota exceeded"
**Solution**: Request GPU quota increase or try different region

### Issue: Model returns errors in predictions
**Solution**: 
- Check endpoint logs: Vertex AI → Endpoints → ⋮ → View logs
- Verify handler.py was uploaded correctly to GCS
- Ensure model artifacts are complete in GCS

### Issue: Chainlit app can't connect
**Solution**:
- Verify GCP_ENDPOINT_ID is set correctly in .env
- Run `gcloud auth login` to refresh authentication
- Check endpoint is deployed and serving

### Issue: "Permission denied" errors
**Solution**:
- Ensure you have Vertex AI User role
- Run: `gcloud auth application-default login`

---

## 📊 Model Lineage

You can view the complete lineage in Vertex AI console:
1. Go to Model Registry → nutrition-assistant-phi3
2. Click on "Lineage" tab
3. You'll see:
   - Pipeline run that created the model
   - Training dataset used
   - All pipeline components
   - Evaluation metrics

---

## 🎉 Success Criteria

- [x] Handler.py created and uploaded to GCS
- [x] Model registered to Vertex AI Model Registry
- [ ] Model deployed to Vertex AI Endpoint (15-30 min)
- [ ] Endpoint tested with curl
- [ ] Chainlit app running and responding to queries
- [ ] Can chat with fine-tuned model through web interface

**Current Status**: Ready for deployment! Follow Step 1 above to deploy to endpoint.

---

## 📚 Additional Resources

- [Vertex AI Model Registry](https://cloud.google.com/vertex-ai/docs/model-registry/introduction)
- [Vertex AI Endpoints](https://cloud.google.com/vertex-ai/docs/predictions/getting-predictions)
- [HuggingFace Containers for Vertex AI](https://github.com/huggingface/Google-Cloud-Containers)
- [Chainlit Documentation](https://docs.chainlit.io/)

---

**Last Updated**: October 21, 2025
**Pipeline Run**: nutrition-assistant-training-pipeline-20251021140422
**Model ID**: 3561348948692041728
