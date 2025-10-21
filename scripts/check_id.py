"""
Vérifier tous les IDs du projet.
"""
import os
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")

aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"\n{'='*80}")
print("🔍 VÉRIFICATION DE L'ID: 3852567797448048640")
print(f"{'='*80}\n")

# Vérifier si c'est un endpoint
print("📍 Vérification des Endpoints:\n")
try:
    endpoints = aiplatform.Endpoint.list()
    for endpoint in endpoints:
        endpoint_id = endpoint.name.split('/')[-1]
        print(f"Endpoint: {endpoint.display_name}")
        print(f"  ID: {endpoint_id}")
        
        if endpoint_id == "3852567797448048640":
            print(f"  ✅ TROUVÉ! C'est cet endpoint!")
            print(f"  URL: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{endpoint_id}?project={PROJECT_ID}")
            
            # Vérifier les modèles déployés
            if endpoint.gca_resource.deployed_models:
                print(f"  Modèles déployés: {len(endpoint.gca_resource.deployed_models)}")
                for dm in endpoint.gca_resource.deployed_models:
                    print(f"    - {dm.display_name}")
            else:
                print(f"  Status: Aucun modèle déployé")
        print()
except Exception as e:
    print(f"Erreur: {e}\n")

# Vérifier si c'est un modèle
print("📦 Vérification des Modèles:\n")
try:
    models = aiplatform.Model.list()
    for model in models:
        model_id = model.name.split('/')[-1].split('@')[0]
        print(f"Modèle: {model.display_name}")
        print(f"  ID: {model_id}")
        
        if model_id == "3852567797448048640":
            print(f"  ✅ TROUVÉ! C'est ce modèle!")
            print(f"  URL: https://console.cloud.google.com/vertex-ai/models/{model_id}/versions?project={PROJECT_ID}")
        print()
except Exception as e:
    print(f"Erreur: {e}\n")

print(f"{'='*80}")
print("📋 RÉCAPITULATIF DE VOS RESSOURCES:")
print(f"{'='*80}\n")

print("Endpoints actifs:")
try:
    endpoints = aiplatform.Endpoint.list()
    for endpoint in endpoints:
        endpoint_id = endpoint.name.split('/')[-1]
        print(f"  - {endpoint.display_name} (ID: {endpoint_id})")
except:
    pass

print("\nModèles enregistrés:")
try:
    models = aiplatform.Model.list(order_by="create_time desc")
    for model in models[:3]:
        model_id = model.name.split('/')[-1].split('@')[0]
        print(f"  - {model.display_name} (ID: {model_id})")
except:
    pass

print(f"\n{'='*80}\n")
