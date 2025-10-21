# 🚀 How to Launch Your Nutrition Assistant

This guide shows you how to easily start and stop your nutrition chatbot to avoid unnecessary costs.

## ⚡ Quick Start (3 Steps)

### 1️⃣ Deploy Model to Endpoint (~5-10 minutes)
```powershell
python scripts/deploy_to_endpoint.py
```
- Deploys your fine-tuned Phi-3 model to Vertex AI
- Creates endpoint with GPU (Tesla T4)
- **Cost:** ~$0.50-$1.00 per hour while deployed

### 2️⃣ Wait for Deployment
```powershell
python scripts/check_endpoint_status.py
```
- Run this to check if deployment is complete
- Look for: "✅ DEPLOYMENT COMPLETE!"
- Status should show: "SERVING"

### 3️⃣ Launch Chatbot Interface
```powershell
python -m chainlit run src/app/main.py -w
```
- Opens web interface at: http://localhost:8000
- Chat with your nutrition model!
- Press `Ctrl+C` in terminal to stop

---

## 🛑 How to Stop (Save Money!)

### Stop the Chatbot (Immediate)
- Press `Ctrl+C` in the terminal where Chainlit is running
- This stops the web interface but model stays deployed

### Stop Billing for Model (IMPORTANT!)
```powershell
python scripts/undeploy_model.py
```
- **Removes model from endpoint**
- **Stops all hourly charges** 💰
- Endpoint remains (empty) for quick redeploy later
- Takes ~2-3 minutes

### Delete Everything (Optional)
```powershell
python scripts/delete_endpoint.py
```
- Completely removes the endpoint
- Use this if you won't use it for a long time
- Type `DELETE` to confirm
- You'll need to recreate endpoint next time

---

## 📊 Cost Breakdown

| Resource | Cost | When Charged |
|----------|------|--------------|
| **Model Deployed** | ~$0.50-$1/hour | While model is on endpoint |
| **Endpoint (empty)** | $0 | No charge if no models deployed |
| **Chatbot UI** | $0 | Running locally on your PC |
| **Storage (GCS)** | ~$0.026/GB/month | Your trained model files |

**💡 Best Practice:** Undeploy model when not using it!

---

## 🔄 Typical Workflow

### Starting a Session
```powershell
# 1. Deploy model (wait 5-10 min)
python scripts/deploy_to_endpoint.py

# 2. Check status until SERVING
python scripts/check_endpoint_status.py

# 3. Launch chatbot
python -m chainlit run src/app/main.py -w

# 4. Open browser to http://localhost:8000
```

### Ending a Session
```powershell
# 1. Stop chatbot (Ctrl+C in Chainlit terminal)

# 2. Undeploy model to stop billing
python scripts/undeploy_model.py
```

---

## 🔧 Troubleshooting

### "Error getting access token"
```powershell
gcloud auth application-default login
```
- Follow browser prompts to authenticate
- Only needed once

### "Endpoint not configured"
- Check `.env` file has `GCP_ENDPOINT_ID=5724492940806455296`
- Restart Chainlit app

### "Model not responding"
```powershell
python scripts/check_endpoint_status.py
```
- Verify model is deployed and status = "SERVING"
- If not deployed, run `python scripts/deploy_to_endpoint.py`

### Chatbot won't start
```powershell
# Make sure packages are installed
pip install chainlit google-auth

# Try running with python -m
python -m chainlit run src/app/main.py -w
```

---

## 📝 File Locations

- **Chatbot App:** `src/app/main.py`
- **Environment:** `.env` (has endpoint ID, project info)
- **Deploy Script:** `scripts/deploy_to_endpoint.py`
- **Undeploy Script:** `scripts/undeploy_model.py`
- **Status Checker:** `scripts/check_endpoint_status.py`

---

## 🎯 Your Endpoint Info

```
Project: aerobic-polygon-460910-v9
Region: europe-west2
Endpoint ID: 5724492940806455296
Endpoint Name: nutrition-assistant-endpoint
Model: nutrition-assistant-phi3 (fine-tuned Phi-3)
Machine: n1-standard-8
GPU: NVIDIA Tesla T4 x1
```

---

## 💡 Pro Tips

1. **Always undeploy** when done testing to avoid charges
2. **Check status** before launching chatbot to ensure model is ready
3. **Keep terminal open** while using chatbot (don't close it)
4. **Model stays warm** for ~30 min after first request (faster responses)
5. **First request** may take 30-60 seconds (model loading)

---

## 🆘 Quick Commands Reference

```powershell
# Deploy model
python scripts/deploy_to_endpoint.py

# Check if ready
python scripts/check_endpoint_status.py

# Launch chatbot
python -m chainlit run src/app/main.py -w

# Stop billing (IMPORTANT!)
python scripts/undeploy_model.py

# Re-authenticate if needed
gcloud auth application-default login
```

---

## 🎉 You're Ready!

Now you can easily:
- ✅ Start your nutrition chatbot in 3 commands
- ✅ Stop billing when not in use
- ✅ Monitor costs and deployment status
- ✅ Troubleshoot common issues

**Enjoy chatting with your AI nutrition assistant! 🥗**
