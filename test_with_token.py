#!/usr/bin/env python3
"""Test avec le token JWT pré-configuré"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def test_with_preconfigured_token():
    try:
        from cli.services.auth import SpiderVisionAuth
        from cli.services.data import SpiderVisionData
        from cli.services.export import DataExporter
        
        print("🔐 Test avec token JWT pré-configuré")
        print("=" * 50)
        
        # Test 1: Authentification avec token pré-configuré
        auth = SpiderVisionAuth()
        print(f"✅ Auth initialisé avec token: {auth._token[:20]}...")
        
        token = auth.login()  # Devrait utiliser le token pré-configuré
        print(f"✅ Token obtenu: {token[:20]}...")
        
        # Test 2: Récupération des données
        data_service = SpiderVisionData()
        overview_data = data_service.get_overview(token)
        print(f"✅ Données récupérées: {type(overview_data)}")
        
        # Test 3: Export
        exporter = DataExporter()
        csv_path = exporter.save_to_csv(overview_data, "test_token_output.csv")
        print(f"✅ CSV exporté: {csv_path}")
        
        print("\n🎉 Test réussi avec le token pré-configuré!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_preconfigured_token()
