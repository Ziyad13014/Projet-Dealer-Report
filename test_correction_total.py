#!/usr/bin/env python3
"""
Test de la correction de l'extraction du total stores
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.repository.WebDataRepository import WebDataRepository
from cli.services.auth import SpiderVisionAuth
from cli.services.data import SpiderVisionData

def test_correction_total():
    """Test de la correction de l'extraction du total stores"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    print("🧪 Test de la correction de l'extraction du total stores")
    print("=" * 60)
    
    try:
        # Initialiser les services
        auth = SpiderVisionAuth()
        data_service = SpiderVisionData()
        repository = WebDataRepository(auth, data_service)
        
        # Authentification
        print("🔐 Authentification...")
        token = auth.login()
        print(f"✅ Token obtenu: {token[:20]}...")
        
        # Récupérer les données overview
        print("\n📊 Récupération des données overview...")
        overview_data = data_service.get_overview(token)
        
        # Parser les données avec la correction
        print("\n🔍 Parsing des données avec la nouvelle logique...")
        retailers = repository._parse_overview_data(overview_data)
        
        print(f"\n📈 Nombre d'enseignes trouvées: {len(retailers)}")
        
        # Afficher les premiers résultats pour vérification
        print("\n🏪 Détails des premières enseignes:")
        print("-" * 80)
        
        for i, retailer in enumerate(retailers[:5]):
            print(f"\n{i+1}. {retailer['name']} (ID: {retailer['retailer_id']})")
            print(f"   📊 Stores crawled: {retailer['stores_crawled']}")
            print(f"   ❌ Stores failed: {retailer['stores_failed']}")
            print(f"   🎯 Total stores: {retailer['stores_total']}")
            print(f"   ✅ Success rate: {retailer['success_rate']:.1f}%")
            print(f"   📈 Progress rate: {retailer['progress_rate']:.1f}%")
            
            # Vérifier la cohérence
            if retailer['stores_total'] > 0:
                calculated_success = (retailer['stores_crawled'] / retailer['stores_total']) * 100
                print(f"   🧮 Success calculé: {calculated_success:.1f}%")
                
                if abs(calculated_success - retailer['success_rate']) > 5:
                    print(f"   ⚠️  Différence significative détectée!")
            
        print("\n" + "=" * 60)
        print("✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correction_total()
