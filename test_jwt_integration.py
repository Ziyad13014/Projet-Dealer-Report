#!/usr/bin/env python3
"""Script de test pour l'intégration complète JWT SpiderVision."""

import os
import sys
from dotenv import load_dotenv

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.services.auth import SpiderVisionAuth
from cli.services.data import SpiderVisionData
from cli.services.export import DataExporter

# Charger les variables d'environnement
load_dotenv()

def test_jwt_integration():
    """Test complet de l'intégration JWT SpiderVision"""
    
    print("🔍 Test d'intégration complète JWT SpiderVision")
    print("=" * 60)
    
    try:
        # Test 1: Authentification
        print("\n📡 Étape 1: Test d'authentification JWT...")
        auth = SpiderVisionAuth()
        
        print(f"API Base: {auth.api_base}")
        print(f"Email: {auth.email}")
        print(f"Login Endpoint: {auth.login_endpoint}")
        
        token = auth.login()
        print(f"✅ Token JWT obtenu: {token[:20]}...{token[-10:]}")
        
        # Test 2: Récupération des données
        print("\n📊 Étape 2: Récupération des données overview...")
        data_service = SpiderVisionData()
        
        print(f"Overview Endpoint: {data_service.overview_endpoint}")
        
        overview_data = data_service.get_overview(token)
        print(f"✅ Données récupérées: {type(overview_data)}")
        print(f"   Taille des données: {len(str(overview_data))} caractères")
        
        if isinstance(overview_data, dict):
            print(f"   Clés principales: {list(overview_data.keys())}")
        elif isinstance(overview_data, list):
            print(f"   Nombre d'éléments: {len(overview_data)}")
            if overview_data:
                print(f"   Premier élément: {type(overview_data[0])}")
                if isinstance(overview_data[0], dict):
                    print(f"   Clés du premier élément: {list(overview_data[0].keys())}")
        
        # Test 3: Export CSV
        print("\n💾 Étape 3: Test d'export CSV...")
        exporter = DataExporter()
        
        csv_path = exporter.save_to_csv(overview_data, "test_overview.csv")
        print(f"✅ Export CSV réussi: {csv_path}")
        
        # Test 4: Export Excel (optionnel)
        print("\n📋 Étape 4: Test d'export Excel...")
        try:
            excel_path = exporter.save_to_excel(overview_data, "test_overview.xlsx")
            print(f"✅ Export Excel réussi: {excel_path}")
        except Exception as e:
            print(f"⚠️ Export Excel échoué (pandas non installé?): {e}")
        
        # Test 5: Test WebDataRepository
        print("\n🏪 Étape 5: Test WebDataRepository avec JWT...")
        from cli.repository.WebDataRepository import WebDataRepository
        
        repo = WebDataRepository()
        dashboard_data = repo.get_dashboard_data()
        
        if dashboard_data:
            print(f"✅ WebDataRepository fonctionne: {len(dashboard_data)} retailers")
            for retailer in dashboard_data[:3]:  # Afficher les 3 premiers
                print(f"   - {retailer['name']}: {retailer['stores_crawled']} crawlés, {retailer['stores_total']} total")
        else:
            print("❌ WebDataRepository n'a pas récupéré de données")
        
        print("\n🎉 Test d'intégration terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_jwt_integration()
    sys.exit(0 if success else 1)
