# 🚀 Comment Lancer Votre Assistant Nutrition

Guide pour démarrer et arrêter facilement votre chatbot nutrition et éviter les coûts inutiles.

## ⚡ Démarrage Rapide (3 Étapes)

### 1️⃣ Déployer le Modèle (~5-10 minutes)
```powershell
python scripts/deploy_to_endpoint.py
```
- Déploie votre modèle Phi-3 fine-tuné sur Vertex AI
- Crée un endpoint avec GPU (Tesla T4)
- **Coût:** ~0,50-1,00$/heure pendant le déploiement

### 2️⃣ Attendre le Déploiement
```powershell
python scripts/check_endpoint_status.py
```
- Vérifiez que le déploiement est terminé
- Cherchez: "✅ DEPLOYMENT COMPLETE!"
- Le statut doit afficher: "SERVING"

### 3️⃣ Lancer l'Interface Chatbot
```powershell
python -m chainlit run src/app/main.py -w
```
- Ouvre l'interface web à: http://localhost:8000
- Discutez avec votre modèle nutrition!
- Appuyez sur `Ctrl+C` pour arrêter

---

## 🛑 Comment Arrêter (Économiser!)

### Arrêter le Chatbot (Immédiat)
- Appuyez sur `Ctrl+C` dans le terminal Chainlit
- Arrête l'interface web mais le modèle reste déployé

### Arrêter la Facturation (IMPORTANT!)
```powershell
python scripts/undeploy_model.py
```
- **Retire le modèle de l'endpoint**
- **Arrête tous les frais horaires** 💰
- L'endpoint reste (vide) pour redéployer rapidement
- Prend ~2-3 minutes

### Tout Supprimer (Optionnel)
```powershell
python scripts/delete_endpoint.py
```
- Supprime complètement l'endpoint
- À utiliser si vous ne l'utilisez pas longtemps
- Tapez `DELETE` pour confirmer
- Vous devrez recréer l'endpoint la prochaine fois

---

## 📊 Détail des Coûts

| Ressource | Coût | Quand Facturé |
|-----------|------|---------------|
| **Modèle Déployé** | ~0,50-1$/heure | Quand le modèle est sur l'endpoint |
| **Endpoint (vide)** | 0$ | Pas de frais si aucun modèle déployé |
| **Interface Chatbot** | 0$ | Tourne localement sur votre PC |
| **Stockage (GCS)** | ~0,026$/GB/mois | Vos fichiers de modèle |

**💡 Bonne Pratique:** Retirer le modèle quand vous ne l'utilisez pas!

---

## 🔄 Flux de Travail Typique

### Démarrer une Session
```powershell
# 1. Déployer le modèle (attendre 5-10 min)
python scripts/deploy_to_endpoint.py

# 2. Vérifier le statut jusqu'à SERVING
python scripts/check_endpoint_status.py

# 3. Lancer le chatbot
python -m chainlit run src/app/main.py -w

# 4. Ouvrir le navigateur à http://localhost:8000
```

### Terminer une Session
```powershell
# 1. Arrêter le chatbot (Ctrl+C dans le terminal Chainlit)

# 2. Retirer le modèle pour arrêter la facturation
python scripts/undeploy_model.py
```

---

## 🔧 Dépannage

### "Error getting access token"
```powershell
gcloud auth application-default login
```
- Suivez les instructions dans le navigateur
- Nécessaire une seule fois

### "Endpoint not configured"
- Vérifiez que `.env` contient `GCP_ENDPOINT_ID=5724492940806455296`
- Redémarrez l'app Chainlit

### "Model not responding"
```powershell
python scripts/check_endpoint_status.py
```
- Vérifiez que le modèle est déployé avec statut "SERVING"
- Sinon, exécutez `python scripts/deploy_to_endpoint.py`

### Le chatbot ne démarre pas
```powershell
# Assurez-vous que les packages sont installés
pip install chainlit google-auth

# Essayez avec python -m
python -m chainlit run src/app/main.py -w
```

---

## 📝 Emplacements des Fichiers

- **App Chatbot:** `src/app/main.py`
- **Environnement:** `.env` (ID endpoint, infos projet)
- **Script Déploiement:** `scripts/deploy_to_endpoint.py`
- **Script Retrait:** `scripts/undeploy_model.py`
- **Vérif. Statut:** `scripts/check_endpoint_status.py`

---

## 🎯 Infos Endpoint

```
Projet: aerobic-polygon-460910-v9
Région: europe-west2
ID Endpoint: 5724492940806455296
Nom Endpoint: nutrition-assistant-endpoint
Modèle: nutrition-assistant-phi3 (Phi-3 fine-tuné)
Machine: n1-standard-8
GPU: NVIDIA Tesla T4 x1
```

---

## 💡 Astuces Pro

1. **Toujours retirer** le modèle après les tests pour éviter les frais
2. **Vérifier le statut** avant de lancer le chatbot
3. **Garder le terminal ouvert** pendant l'utilisation du chatbot
4. **Le modèle reste chaud** ~30 min après la 1ère requête (réponses plus rapides)
5. **1ère requête** peut prendre 30-60 secondes (chargement du modèle)

---

## 🆘 Commandes de Référence Rapide

```powershell
# Déployer le modèle
python scripts/deploy_to_endpoint.py

# Vérifier si prêt
python scripts/check_endpoint_status.py

# Lancer le chatbot
python -m chainlit run src/app/main.py -w

# Arrêter la facturation (IMPORTANT!)
python scripts/undeploy_model.py

# Ré-authentifier si besoin
gcloud auth application-default login
```

---

## 🎉 Vous êtes Prêt!

Maintenant vous pouvez facilement:
- ✅ Démarrer votre chatbot nutrition en 3 commandes
- ✅ Arrêter la facturation quand inutilisé
- ✅ Surveiller les coûts et le statut
- ✅ Résoudre les problèmes courants

**Profitez de votre assistant nutrition IA! 🥗**
