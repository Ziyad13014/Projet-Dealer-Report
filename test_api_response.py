#!/usr/bin/env python3
"""Test pour voir la structure des données de l'API SpiderVision"""

import requests
import json
import os
from dotenv import load_dotenv

def test_api():
    load_dotenv()
    
    # Récupérer le token ou se connecter
    token = os.getenv('SPIDER_VISION_JWT_TOKEN')
    if not token:
        print("⚠️ Token non trouvé dans .env, tentative de connexion...")
        try:
            from cli.services.auth import SpiderVisionAuth
            auth = SpiderVisionAuth()
            token = auth.login()
            print("✅ Connexion réussie, nouveau token obtenu")
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return
    
    # Récupérer les données
    url = os.getenv('SPIDER_VISION_API_BASE')
    overview_url = f"{url}/store-history/overview"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    print(f"🔄 Requête vers: {overview_url}")
    
    try:
        response = requests.get(overview_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Afficher la structure
        print("\n✅ Données reçues avec succès!")
        print(f"Type de données: {type(data)}")
        
        if isinstance(data, list):
            print(f"Nombre d'éléments: {len(data)}")
            if len(data) > 0:
                print("\n📋 Premier élément:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
        elif isinstance(data, dict):
            print(f"Clés disponibles: {list(data.keys())}")
            print("\n📋 Données complètes (premiers 2000 caractères):")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        
        # Chercher Carrefour
        print("\n\n🔍 Recherche de Carrefour...")
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    name = item.get('name', item.get('domainDealerName', ''))
                    if 'Carrefour' in str(name):
                        print(f"\n🎯 Trouvé: {name}")
                        print(json.dumps(item, indent=2, ensure_ascii=False))
                        break
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_api()
