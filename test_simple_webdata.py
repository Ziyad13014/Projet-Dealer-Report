#!/usr/bin/env python3
"""Test simple pour WebDataRepository"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def main():
    try:
        print("🧪 Test simple WebDataRepository...")
        
        # Import des modules
        from cli.repository.WebDataRepository import WebDataRepository
        
        # Créer le repository
        repo = WebDataRepository()
        print("✅ Repository créé")
        
        # Test avec un retailer simple
        retailer = "leclerc"
        print(f"\n🔍 Test extraction pour '{retailer}':")
        
        # Test crawling data
        crawling_data = repo.get_crawling_counters(retailer)
        print(f"📊 Crawling data: {crawling_data}")
        
        # Vérifier les champs importants
        if crawling_data:
            print(f"   • Total stores: {crawling_data.get('total_stores', 'N/A')}")
            print(f"   • Stores crawled: {crawling_data.get('stores_crawled', 'N/A')}")
            print(f"   • Success rate: {crawling_data.get('success_rate', 'N/A')}%")
            print(f"   • Progress rate: {crawling_data.get('progress_rate', 'N/A')}%")
        
        # Test content data
        content_data = repo.get_content_counters(retailer)
        print(f"📋 Content data: {content_data}")
        
        if content_data:
            print(f"   • Success rate content: {content_data.get('success_rate', 'N/A')}%")
        
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
