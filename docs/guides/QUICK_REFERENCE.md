# ⚡ QUICK REFERENCE - Nutrition Assistant

## 🟢 START (3 commands)
```powershell
python scripts/deploy_to_endpoint.py          # Wait 5-10 min
python scripts/check_endpoint_status.py        # Check = SERVING
python -m chainlit run src/app/main.py -w      # Open http://localhost:8000
```

## 🔴 STOP (2 commands)
```powershell
Ctrl+C                                         # Stop chatbot UI
python scripts/undeploy_model.py               # STOP BILLING 💰
```

---

## 📋 All Commands

| Command | What It Does | Time |
|---------|-------------|------|
| `python scripts/deploy_to_endpoint.py` | Deploy model to endpoint | 5-10 min |
| `python scripts/check_endpoint_status.py` | Check deployment status | <5 sec |
| `python -m chainlit run src/app/main.py -w` | Launch chatbot UI | <5 sec |
| `python scripts/undeploy_model.py` | **Stop billing** | 2-3 min |
| `python scripts/delete_endpoint.py` | Delete endpoint completely | 1-2 min |
| `gcloud auth application-default login` | Re-authenticate (if needed) | 30 sec |

---

## 💰 Costs

| Status | Cost/Hour |
|--------|-----------|
| ✅ Model deployed | $0.50-$1.00 |
| ⚪ Endpoint empty | $0.00 |
| ❌ Undeployed | $0.00 |

**⚠️ ALWAYS undeploy when done!**

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Error getting access token" | `gcloud auth application-default login` |
| "Endpoint not configured" | Check `.env` has `GCP_ENDPOINT_ID=5724492940806455296` |
| Model not responding | Run `python scripts/check_endpoint_status.py` |
| Chainlit won't start | Run `pip install chainlit google-auth` |

---

## 📍 Your Setup

```
Endpoint ID: 5724492940806455296
URL: http://localhost:8000
Model: nutrition-assistant-phi3
GPU: Tesla T4
```

---

## 💡 Remember

1. First request = 30-60 sec (model loading)
2. Always check status before launching chatbot
3. **Undeploy = save money!** 💰
4. Keep terminal open while using chatbot

---

**Made with ❤️ for Albert School LLM OPS Bootcamp**
