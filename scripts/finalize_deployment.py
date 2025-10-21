"""
Script pour finaliser le déploiement sur l'endpoint existant.
"""
import os
from google.cloud import aiplatform
from dotenv import load_dotenv
import time

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")
MODEL_ID = "3561348948692041728"
ENDPOINT_ID = "5724492940806455296"

aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"\n{'='*80}")
print("🚀 Finalisation du déploiement")
print(f"{'='*80}\n")

# Charger le modèle et l'endpoint
print("📦 Chargement du modèle...")
model = aiplatform.Model(f"projects/432566588992/locations/{REGION}/models/{MODEL_ID}")
print(f"✅ Modèle: {model.display_name}\n")

print("📍 Chargement de l'endpoint...")
endpoint = aiplatform.Endpoint(f"projects/432566588992/locations/{REGION}/endpoints/{ENDPOINT_ID}")
print(f"✅ Endpoint: {endpoint.display_name}\n")

# Vérifier si déjà déployé
if endpoint.gca_resource.deployed_models:
    print("✅ Le modèle est déjà déployé!")
    for dm in endpoint.gca_resource.deployed_models:
        print(f"   - {dm.display_name}")
    print(f"\n🔗 Console: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}")
else:
    print("⏳ Déploiement du modèle sur l'endpoint...")
    print("   Configuration: n1-standard-8 + NVIDIA Tesla T4")
    print("   Temps estimé: 15-30 minutes")
    print(f"\n🔗 Suivre dans la console: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}\n")
    
    # Déployer sans attendre (async)
    print("🚀 Démarrage du déploiement en arrière-plan...")
    
    deployed_model = model.deploy(
        endpoint=endpoint,
        deployed_model_display_name=f"{model.display_name}-deployment",
        machine_type="n1-standard-8",
        accelerator_type="NVIDIA_TESLA_T4",
        accelerator_count=1,
        min_replica_count=1,
        max_replica_count=1,
        traffic_percentage=100,
        sync=False,  # Ne pas attendre - déploiement async
    )
    
    print("\n✅ Déploiement lancé avec succès!")
    print(f"\n{'='*80}")
    print("📊 PROCHAINES ÉTAPES:")
    print(f"{'='*80}\n")
    print("1. Le déploiement continue en arrière-plan (15-30 min)")
    print(f"2. Surveillez ici: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}")
    print("3. Attendez que le statut soit 'Serving' (vert)")
    print("4. Ensuite, mettez à jour .env avec:")
    print(f"   GCP_ENDPOINT_ID={ENDPOINT_ID}")
    print(f"   GCP_PROJECT_NUMBER=432566588992")
    print("5. Testez avec: chainlit run src/app/main.py -w")
    print(f"\n{'='*80}\n")

print(f"\n{'='*80}")
print("🔗 URLS UTILES:")
print(f"{'='*80}\n")
print(f"Vertex AI: https://console.cloud.google.com/vertex-ai?project={PROJECT_ID}")
print(f"Endpoints: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints?project={PROJECT_ID}")
print(f"Votre endpoint: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}")
print(f"\n{'='*80}\n")
