#!/usr/bin/env python3
"""Test pour vérifier l'extraction du pourcentage de succès dans WebDataRepository"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def test_webdata_parsing():
    try:
        print("🔄 Test de WebDataRepository avec les nouvelles modifications...")
        
        from cli.repository.WebDataRepository import WebDataRepository
        
        # Créer une instance du repository
        repo = WebDataRepository()
        
        print("✅ Repository créé")
        
        # Tester l'extraction des données
        print("📊 Test d'extraction des données...")
        
        # Obtenir les données de crawling pour quelques retailers
        test_retailers = ['leclerc', 'carrefour', 'biocoop']
        
        for retailer in test_retailers:
            print(f"\n🔍 Test pour {retailer}:")
            
            try:
                # Tester get_crawling_counters
                crawling_data = repo.get_crawling_counters(retailer)
                print(f"   📈 Crawling: {crawling_data}")
                
                # Tester get_content_counters  
                content_data = repo.get_content_counters(retailer)
                print(f"   📋 Content: {content_data}")
                
                # Vérifier les pourcentages de succès
                if 'success_rate' in crawling_data:
                    print(f"   ✅ Success rate crawling: {crawling_data['success_rate']}%")
                
                if 'success_rate' in content_data:
                    print(f"   ✅ Success rate content: {content_data['success_rate']}%")
                    
            except Exception as e:
                print(f"   ❌ Erreur pour {retailer}: {e}")
        
        print(f"\n🎯 Test terminé!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_webdata_parsing()
