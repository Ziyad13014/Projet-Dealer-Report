#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour tester la validité d'un token JWT avec l'API SpiderVision
"""

import sys
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_token():
    """Teste le token JWT actuel"""
    
    # Charger les variables d'environnement
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    token = os.getenv('SPIDER_VISION_JWT_TOKEN', '').strip()
    api_base = os.getenv('SPIDER_VISION_API_BASE', 'https://food-api-spider-vision.data-solutions.com')
    overview_endpoint = os.getenv('SPIDER_VISION_OVERVIEW_ENDPOINT', '/store-history/overview')
    
    print("🧪 TEST DU TOKEN JWT")
    print("=" * 80)
    
    if not token:
        print("❌ Aucun token trouvé dans .env")
        print("💡 Exécutez d'abord: python scripts\\generer_nouveau_token.py")
        return False
    
    print(f"📍 API Base: {api_base}")
    print(f"📍 Endpoint: {overview_endpoint}")
    print(f"🔑 Token (premiers 50 chars): {token[:50]}...")
    print("=" * 80)
    
    # Test 1: Vérifier le format du token
    print("\n📋 Test 1: Format du token")
    if token.count('.') == 2:
        print("   ✅ Format JWT valide (3 parties séparées par des points)")
    else:
        print("   ❌ Format JWT invalide")
        return False
    
    # Test 2: Tester l'authentification
    print("\n📋 Test 2: Authentification avec l'API")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    url = f"{api_base}{overview_endpoint}"
    print(f"   🔄 Requête GET vers: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Authentification réussie !")
            
            # Test 3: Vérifier les données
            print("\n📋 Test 3: Validation des données")
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"   ✅ Données reçues: {len(data)} retailers")
                    
                    # Afficher un exemple
                    first_item = data[0]
                    print(f"   📦 Premier retailer: {first_item.get('domain', 'N/A')}")
                    print(f"   📊 Progress: {first_item.get('globalProgress', 'N/A')}%")
                    print(f"   📊 Success: {first_item.get('successRate', 'N/A')}%")
                    
                    print("\n" + "=" * 80)
                    print("🎉 TOKEN VALIDE ET FONCTIONNEL !")
                    print("=" * 80)
                    print("\n✅ Vous pouvez maintenant générer un rapport:")
                    print("   → python src\\generate_new_report.py")
                    print("   → scripts\\lancer_rapport.bat")
                    return True
                else:
                    print("   ⚠️ Données reçues mais format inattendu")
                    print(f"   Type: {type(data)}")
                    return False
            except Exception as e:
                print(f"   ❌ Erreur parsing JSON: {e}")
                return False
                
        elif response.status_code == 401:
            print("   ❌ Token expiré ou invalide (401 Unauthorized)")
            print("\n💡 Solution: Générez un nouveau token:")
            print("   → python scripts\\generer_nouveau_token.py")
            return False
            
        else:
            print(f"   ❌ Erreur inattendue: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    try:
        success = test_token()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        sys.exit(1)
