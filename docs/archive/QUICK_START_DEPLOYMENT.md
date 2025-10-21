# ⚡ Quick Start - Deploy Your Nutrition Assistant

## 🎯 You Are Here
✅ Pipeline trained successfully  
✅ Model registered to Vertex AI  
📍 **Ready to deploy!**

---

## 🚀 5-Minute Deployment Checklist

### 1️⃣ Deploy to Endpoint (Console - Start This Now!)
**This takes 15-30 minutes, so start it while you prepare other things.**

1. Open this link: https://console.cloud.google.com/vertex-ai/models/3561348948692041728?project=aerobic-polygon-460910-v9

2. Click the **⋮** (three dots) → **"Deploy to endpoint"**

3. Create new endpoint:
   - Name: `nutrition-assistant-endpoint`
   - Region: `europe-west2`
   - Click **Continue**

4. Configure:
   - Traffic: 100% (default)
   - Machine: **n1-standard-8**
   - Accelerator: **NVIDIA Tesla T4** (quantity: 1)
   - Min/Max nodes: **1** and **1**
   - Click **Deploy**

⏰ **Wait 15-30 minutes** while endpoint deploys. Check logs: Click ⋮ → "View logs"

---

### 2️⃣ Update .env File

While waiting, add these to your `.env` file:

```bash
GCP_PROJECT_NUMBER=432566588992
GCP_ENDPOINT_ID=  # You'll get this after deployment completes
```

---

### 3️⃣ Install Chainlit (While Waiting)

```powershell
pip install chainlit requests
```

---

### 4️⃣ Get Endpoint ID (After Deployment)

Once deployment completes:
1. Go to: https://console.cloud.google.com/vertex-ai/endpoints?project=aerobic-polygon-460910-v9
2. Click on `nutrition-assistant-endpoint`
3. Copy the **endpoint ID** (numbers at the end)
4. Paste into `.env` file: `GCP_ENDPOINT_ID=your-id-here`

---

### 5️⃣ Test It!

**Option A: Quick Test**
```powershell
python scripts/test_endpoint.py --prompt "What are the benefits of spinach?"
```

**Option B: Web Interface**
```powershell
chainlit run src/app/main.py -w
```
Opens at: http://localhost:8000 🎉

---

## 📋 What Was Built For You

### ✅ All 4 Session 4 Tasks Complete

1. **`src/handler.py`** - Custom endpoint handler for Vertex AI
2. **`scripts/register_model_with_custom_handler.py`** - Model registration (DONE)
3. **Model Registered** - ID: 3561348948692041728 ✅
4. **`src/app/main.py`** - Full Chainlit web app

### 📁 New Files Created
```
src/
├── handler.py                                     ✅ Production-ready
└── app/
    └── main.py                                    ✅ Web interface

scripts/
├── register_model_with_custom_handler.py          ✅ Used successfully
├── test_endpoint.py                               ✅ Testing tool
├── get_task_details.py                            ✅ Helper
└── find_model_uri.py                              ✅ Helper

sample_input.json                                  ✅ Test data
SESSION4_DEPLOYMENT_GUIDE.md                       ✅ Full guide
SESSION4_IMPLEMENTATION_SUMMARY.md                 ✅ Complete summary
```

---

## 🎮 Try These Questions

Once your app is running:

1. "What are the nutritional benefits of spinach?"
2. "What are some high-protein foods?"
3. "Which foods are rich in vitamin C?"
4. "Can you suggest healthy snack options?"
5. "How much protein is in chicken breast?"
6. "What are the health benefits of broccoli?"

---

## ⚠️ Don't Forget!

**Delete endpoint after testing to avoid costs:**
1. Go to Vertex AI → Endpoints
2. Select your endpoint
3. Click **"Undeploy model"**
4. Click **"Delete endpoint"**

**Cost**: ~$0.50-$1.00 per hour while running

---

## 🆘 Troubleshooting

### Deployment Failed?
- Check GPU quota: IAM & Admin → Quotas → "NVIDIA T4"
- Try different region if quota unavailable
- Check logs in deployment page

### Endpoint Returns Errors?
```powershell
# Check endpoint logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" --limit 50
```

### Can't Connect?
```powershell
# Refresh authentication
gcloud auth login
gcloud auth application-default login
```

---

## 📚 Full Documentation

For detailed information, see:
- **`SESSION4_DEPLOYMENT_GUIDE.md`** - Complete deployment guide
- **`SESSION4_IMPLEMENTATION_SUMMARY.md`** - Technical details
- **`session4_practice.md`** - Original requirements

---

## 🎉 You're Almost Done!

**Current Status:**
- ✅ Pipeline trained (1.5 hours) - DONE
- ✅ Model registered to Vertex AI - DONE
- ⏳ Deploy endpoint (15-30 min) - **START THIS NOW**
- ✅ Web app ready - DONE
- 🎯 Test and chat with your model - **READY**

**Start the deployment now and come back in 20 minutes! ⏰**

---

**Model**: nutrition-assistant-phi3 (Phi-3 + LoRA)  
**Trained on**: 2,395 nutrition conversations  
**Ready for**: Real-time nutrition Q&A 🥗
