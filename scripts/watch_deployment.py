"""
Surveiller le déploiement en temps réel.
"""
import os
import time
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
REGION = os.getenv("GCP_REGION", "europe-west2")
ENDPOINT_ID = "5724492940806455296"

aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"\n{'='*80}")
print(f"⏳ SURVEILLANCE DU DÉPLOIEMENT")
print(f"{'='*80}\n")
print(f"Endpoint: nutrition-assistant-endpoint")
print(f"ID: {ENDPOINT_ID}")
print(f"Région: {REGION}\n")
print(f"🔗 Console: https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}\n")
print(f"{'='*80}\n")

print("🔄 Vérification toutes les 30 secondes...")
print("   Appuyez sur Ctrl+C pour arrêter\n")

check_count = 0
start_time = time.time()

try:
    while True:
        check_count += 1
        elapsed = time.time() - start_time
        
        print(f"[{time.strftime('%H:%M:%S')}] Check #{check_count} (après {int(elapsed/60)} min {int(elapsed%60)} sec)")
        
        try:
            endpoint = aiplatform.Endpoint(f"projects/432566588992/locations/{REGION}/endpoints/{ENDPOINT_ID}")
            
            if endpoint.gca_resource.deployed_models:
                print(f"\n{'='*80}")
                print("✅ DÉPLOIEMENT TERMINÉ!")
                print(f"{'='*80}\n")
                
                for deployed_model in endpoint.gca_resource.deployed_models:
                    print(f"📦 Modèle déployé:")
                    print(f"   Nom: {deployed_model.display_name}")
                    print(f"   ID: {deployed_model.id}")
                    
                    if hasattr(deployed_model, 'dedicated_resources'):
                        if deployed_model.dedicated_resources.machine_spec:
                            print(f"   Machine: {deployed_model.dedicated_resources.machine_spec.machine_type}")
                            if deployed_model.dedicated_resources.machine_spec.accelerator_type:
                                accel = deployed_model.dedicated_resources.machine_spec.accelerator_type
                                count = deployed_model.dedicated_resources.machine_spec.accelerator_count
                                print(f"   GPU: {accel} x {count}")
                    print()
                
                print(f"⏱️  Temps total: {int(elapsed/60)} minutes {int(elapsed%60)} secondes\n")
                print(f"{'='*80}")
                print("🧪 TESTEZ MAINTENANT!")
                print(f"{'='*80}\n")
                print("Option 1 - Test rapide:")
                print('  python scripts/test_endpoint.py --prompt "What are the benefits of spinach?"\n')
                print("Option 2 - Interface web:")
                print("  chainlit run src/app/main.py -w")
                print("  Puis allez sur: http://localhost:8000\n")
                print(f"{'='*80}\n")
                break
            else:
                print(f"   ⏳ Toujours en cours de déploiement...")
                print(f"   Prochaine vérification dans 30 secondes...\n")
                
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la vérification: {e}")
            print(f"   Nouvelle tentative dans 30 secondes...\n")
        
        time.sleep(30)
        
except KeyboardInterrupt:
    print(f"\n\n{'='*80}")
    print("⏸️  Surveillance arrêtée par l'utilisateur")
    print(f"{'='*80}\n")
    print(f"Temps écoulé: {int(elapsed/60)} minutes {int(elapsed%60)} secondes")
    print(f"\nVous pouvez relancer ce script à tout moment:")
    print(f"  python scripts/check_endpoint_status.py\n")
    print(f"Ou vérifier dans la console:")
    print(f"  https://console.cloud.google.com/vertex-ai/online-prediction/endpoints/{ENDPOINT_ID}?project={PROJECT_ID}\n")
    print(f"{'='*80}\n")
