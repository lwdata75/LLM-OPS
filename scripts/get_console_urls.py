"""
Script pour obtenir les vraies URLs de la console GCP.
"""
import os
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")

aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"\n{'='*80}")
print("🔗 VRAIES URLs DE LA CONSOLE GCP")
print(f"{'='*80}\n")

# URLs principales
print("📍 VERTEX AI - PAGES PRINCIPALES:\n")

print("1. Vertex AI - Vue d'ensemble:")
print(f"   https://console.cloud.google.com/vertex-ai?project={PROJECT_ID}\n")

print("2. Model Registry:")
print(f"   https://console.cloud.google.com/vertex-ai/models?project={PROJECT_ID}\n")

print("3. Endpoints:")
print(f"   https://console.cloud.google.com/vertex-ai/online-prediction/endpoints?project={PROJECT_ID}\n")

print("4. Pipelines:")
print(f"   https://console.cloud.google.com/vertex-ai/pipelines/runs?project={PROJECT_ID}\n")

# Vérifier les modèles
print(f"\n{'='*80}")
print("📦 VOS MODÈLES:")
print(f"{'='*80}\n")

try:
    models = aiplatform.Model.list(order_by="create_time desc")
    for i, model in enumerate(models[:3], 1):
        model_id = model.name.split('/')[-1].split('@')[0]
        print(f"{i}. {model.display_name}")
        print(f"   ID: {model_id}")
        print(f"   URL: https://console.cloud.google.com/vertex-ai/models/{model_id}/versions?project={PROJECT_ID}\n")
except Exception as e:
    print(f"   ⚠️ Erreur: {e}\n")

# Vérifier les endpoints
print(f"{'='*80}")
print("🎯 VOS ENDPOINTS:")
print(f"{'='*80}\n")

try:
    endpoints = aiplatform.Endpoint.list(order_by="create_time desc")
    if endpoints:
        for i, endpoint in enumerate(endpoints[:3], 1):
            endpoint_id = endpoint.name.split('/')[-1]
            print(f"{i}. {endpoint.display_name}")
            print(f"   ID: {endpoint_id}")
            print(f"   URL: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{endpoint_id}?project={PROJECT_ID}")
            print(f"   Région: {REGION}")
            
            # Vérifier les modèles déployés
            if endpoint.gca_resource.deployed_models:
                print(f"   Modèles déployés: {len(endpoint.gca_resource.deployed_models)}")
            else:
                print(f"   ⚠️ Aucun modèle déployé sur cet endpoint")
            print()
    else:
        print("   Aucun endpoint trouvé.\n")
except Exception as e:
    print(f"   ⚠️ Erreur: {e}\n")

print(f"{'='*80}")
print("💡 CONSEIL:")
print(f"{'='*80}\n")
print("Si les URLs ne marchent pas, essayez:")
print("1. Vérifiez que vous êtes connecté au bon projet GCP")
print("2. Allez directement sur: https://console.cloud.google.com")
print("3. Sélectionnez le projet: aerobic-polygon-460910-v9")
print("4. Dans le menu, cherchez 'Vertex AI'")
print(f"\n{'='*80}\n")
