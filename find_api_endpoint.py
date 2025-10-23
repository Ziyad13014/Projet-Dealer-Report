#!/usr/bin/env python3
"""Trouve l'endpoint API utilisé par SpiderVision"""

import requests
from dotenv import load_dotenv
import os

load_dotenv()

def find_api_endpoint():
    print("\n🔍 Recherche de l'endpoint API...\n")
    
    # Authentification
    from cli.services.auth import SpiderVisionAuth
    auth = SpiderVisionAuth()
    token = auth.login()
    print("✅ Authentifié\n")
    
    # Liste des endpoints à tester
    base_url = 'https://spider-vision.data-solutions.com'
    api_base = 'https://food-api-spider-vision.data-solutions.com'
    
    endpoints_to_test = [
        f"{api_base}/store-history/overview",
        f"{api_base}/api/store-history/overview",
        f"{api_base}/api/overview",
        f"{api_base}/api/stores",
        f"{api_base}/overview",
        f"{base_url}/api/overview",
        f"{base_url}/api/stores",
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    print("🎯 Test des endpoints API:\n")
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"✅ TROUVÉ ! {endpoint}")
                        print(f"   Type: liste de {len(data)} éléments")
                        print(f"   Exemple de clés: {list(data[0].keys())[:5]}")
                        return endpoint
                    elif isinstance(data, dict):
                        print(f"✅ TROUVÉ ! {endpoint}")
                        print(f"   Type: dictionnaire")
                        print(f"   Clés: {list(data.keys())[:5]}")
                        return endpoint
                except:
                    print(f"⚠️  {endpoint} - Réponse 200 mais pas JSON")
            elif response.status_code == 401:
                print(f"🔒 {endpoint} - Unauthorized (401)")
            elif response.status_code == 404:
                print(f"❌ {endpoint} - Not Found (404)")
            else:
                print(f"⚠️  {endpoint} - Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Erreur: {str(e)[:50]}")
    
    print("\n❌ Aucun endpoint fonctionnel trouvé")
    return None

if __name__ == "__main__":
    endpoint = find_api_endpoint()
    if endpoint:
        print(f"\n💡 Utilisez cet endpoint: {endpoint}")