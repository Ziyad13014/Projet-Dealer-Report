#!/usr/bin/env python3
"""Script de test pour la récupération des données du tableau Spider Vision."""

import os
import sys
from dotenv import load_dotenv

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.repository.WebDataRepository import WebDataRepository

# Charger les variables d'environnement
load_dotenv()

def test_dashboard_data_extraction():
    """Tester la récupération des données du tableau dashboard"""
    
    base_url = os.getenv('SPIDER_VISION_URL', 'https://spider-vision.data-solutions.com/#/login')
    username = os.getenv('SPIDER_VISION_USERNAME', 'crawl@wiser.com')
    password = os.getenv('SPIDER_VISION_PASSWORD', 'cra@01012024?')
    
    print("🔍 Test de récupération des données du tableau Spider Vision")
    print(f"URL: {base_url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print("-" * 60)
    
    # Créer le repository
    repo = WebDataRepository(base_url, username, password)
    
    try:
        print("📡 Étape 1: Test d'authentification...")
        if repo._authenticate():
            print("✅ Authentification réussie!")
        else:
            print("❌ Échec d'authentification")
            return
        
        print("\n📊 Étape 2: Récupération des données du dashboard...")
        dashboard_data = repo.get_dashboard_data()
        
        if dashboard_data:
            print(f"✅ Trouvé {len(dashboard_data)} retailers dans le dashboard:")
            print()
            
            for retailer in dashboard_data:
                print(f"🏪 {retailer['name']} (ID: {retailer['id']})")
                print(f"   - Magasins crawlés: {retailer['stores_crawled']}")
                print(f"   - Magasins en échec: {retailer['stores_failed']}")
                print(f"   - Total magasins: {retailer['stores_total']}")
                print(f"   - Taux de succès: {retailer['success_rate']}%")
                print(f"   - Taux de progression: {retailer['progress_rate']}%")
                print()
        else:
            print("❌ Aucune donnée récupérée du dashboard")
            
        print("\n🔧 Étape 3: Test des méthodes spécialisées...")
        
        if dashboard_data:
            # Tester avec le premier retailer trouvé
            test_retailer = dashboard_data[0]['name']
            print(f"Test avec le retailer: {test_retailer}")
            
            from datetime import datetime, date
            today = date.today()
            
            # Test crawling counters
            crawling_data = repo.get_crawling_counters(test_retailer, today, today)
            print(f"   - Crawling counters: {crawling_data}")
            
            # Test content counters
            content_data = repo.get_content_counters(test_retailer, today, today)
            print(f"   - Content counters: {content_data}")
            
            # Test progress at 09:30
            progress = repo.get_progress_at_0930(test_retailer, datetime.now())
            print(f"   - Progress at 09:30: {progress}%")
            
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_data_extraction()
