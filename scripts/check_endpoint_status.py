"""
Vérifier le statut détaillé de l'endpoint et des modèles déployés.
"""
import os
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")
ENDPOINT_ID = "5724492940806455296"

aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"\n{'='*80}")
print(f"🔍 STATUT DE L'ENDPOINT: {ENDPOINT_ID}")
print(f"{'='*80}\n")

try:
    # Charger l'endpoint
    endpoint = aiplatform.Endpoint(f"projects/432566588992/locations/{REGION}/endpoints/{ENDPOINT_ID}")
    
    print(f"📍 Endpoint: {endpoint.display_name}")
    print(f"   ID: {ENDPOINT_ID}")
    print(f"   Région: {REGION}")
    print(f"   Resource: {endpoint.resource_name}\n")
    
    # Vérifier les modèles déployés
    print(f"{'='*80}")
    print("📦 MODÈLES DÉPLOYÉS:")
    print(f"{'='*80}\n")
    
    if endpoint.gca_resource.deployed_models:
        print(f"✅ {len(endpoint.gca_resource.deployed_models)} modèle(s) déployé(s):\n")
        
        for i, deployed_model in enumerate(endpoint.gca_resource.deployed_models, 1):
            print(f"{i}. Deployed Model:")
            print(f"   Nom: {deployed_model.display_name}")
            print(f"   ID du modèle déployé: {deployed_model.id}")
            print(f"   Modèle source: {deployed_model.model}")
            
            # Extraire l'ID du modèle source
            if deployed_model.model:
                source_model_id = deployed_model.model.split('/')[-1].split('@')[0]
                print(f"   ID du modèle source: {source_model_id}")
            
            # Traffic split
            if hasattr(deployed_model, 'traffic_split'):
                print(f"   Traffic: {deployed_model.traffic_split}%")
            
            # Machine type
            if hasattr(deployed_model, 'dedicated_resources'):
                if deployed_model.dedicated_resources.machine_spec:
                    print(f"   Machine: {deployed_model.dedicated_resources.machine_spec.machine_type}")
                    if deployed_model.dedicated_resources.machine_spec.accelerator_type:
                        print(f"   GPU: {deployed_model.dedicated_resources.machine_spec.accelerator_type} x {deployed_model.dedicated_resources.machine_spec.accelerator_count}")
                if deployed_model.dedicated_resources.min_replica_count:
                    print(f"   Replicas: {deployed_model.dedicated_resources.min_replica_count}")
            
            print()
            
            # Vérifier si c'est l'ID mentionné
            if deployed_model.id == "3852567797448048640":
                print(f"   🎯 ✅ OUI! C'est l'ID du modèle déployé que vous avez mentionné!")
                print()
        
        print(f"{'='*80}")
        print("✅ DÉPLOIEMENT TERMINÉ!")
        print(f"{'='*80}\n")
        print("Votre endpoint est prêt à recevoir des requêtes! 🎉\n")
        print("🔗 Console: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}\n")
        print("Testez maintenant:")
        print("  python scripts/test_endpoint.py")
        print("  OU")
        print("  chainlit run src/app/main.py -w\n")
        
    else:
        print("⏳ Aucun modèle déployé encore.")
        print("   Le déploiement est toujours en cours...")
        print(f"   Surveillez: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}\n")
    
    print(f"{'='*80}\n")
    
except Exception as e:
    print(f"❌ Erreur: {e}\n")
    import traceback
    traceback.print_exc()
