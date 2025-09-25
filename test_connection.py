#!/usr/bin/env python3
"""Script de test pour vérifier la connexion à Spider Vision."""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from cli.repository.WebDataRepository import WebDataRepository
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_spider_vision_connection():
    """Tester la connexion à Spider Vision."""
    load_dotenv()
    
    # Récupérer les credentials depuis .env
    url = os.getenv('SPIDER_VISION_URL')
    username = os.getenv('SPIDER_VISION_USERNAME')
    password = os.getenv('SPIDER_VISION_PASSWORD')
    
    print(f"🔗 Test de connexion à Spider Vision")
    print(f"URL: {url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'NON DÉFINI'}")
    print("-" * 50)
    
    if not all([url, username, password]):
        print("❌ Credentials manquants dans .env")
        return False
    
    # Créer le repository
    repo = WebDataRepository(url, username, password)
    
    # Test 1: Authentification
    print("🔐 Test d'authentification...")
    auth_success = repo._authenticate()
    if auth_success:
        print("✅ Authentification réussie")
    else:
        print("❌ Échec de l'authentification")
        return False
    
    # Test 2: Récupération des règles retailers
    print("\n📋 Test de récupération des règles retailers...")
    try:
        rules = repo.get_retailer_rules()
        print(f"✅ {len(rules)} règles récupérées:")
        for rule in rules[:3]:  # Afficher les 3 premières
            print(f"  - {rule['retailer_name']}: success_rate≥{rule['min_success_rate']}%, progress≥{rule['min_progress_0930']}%")
        if len(rules) > 3:
            print(f"  ... et {len(rules) - 3} autres")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des règles: {e}")
        return False
    
    # Test 3: Test d'un endpoint de données
    print("\n📊 Test de récupération de données...")
    try:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # Tester avec le premier retailer
        if rules:
            retailer_name = rules[0]['retailer_name']
            print(f"Test avec retailer: {retailer_name}")
            
            counters = repo.get_success_counters(retailer_name, start_date, end_date)
            print(f"✅ Compteurs récupérés: {counters['success_count']}/{counters['total_count']}")
            
            progress = repo.get_progress_at_0930(retailer_name, end_date)
            print(f"✅ Progrès à 09:30: {progress:.1f}%")
        else:
            print("⚠️ Aucun retailer disponible pour le test")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {e}")
        return False
    
    print("\n🎉 Tous les tests sont passés avec succès!")
    return True

if __name__ == "__main__":
    success = test_spider_vision_connection()
    sys.exit(0 if success else 1)
