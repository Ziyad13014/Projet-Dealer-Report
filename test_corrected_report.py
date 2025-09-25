#!/usr/bin/env python3
"""Test pour générer un rapport avec les données corrigées du WebDataRepository"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def main():
    try:
        print("🔄 Test du rapport avec WebDataRepository corrigé...")
        
        # Import des modules
        from cli.services.ReportService import ReportService
        from cli.repository.WebDataRepository import WebDataRepository
        from cli.ioc import Container
        
        # Configurer le container
        container = Container()
        container.config.from_dict({
            'spider_vision': {
                'url': os.getenv('SPIDER_VISION_URL'),
                'username': os.getenv('SPIDER_VISION_USERNAME'), 
                'password': os.getenv('SPIDER_VISION_PASSWORD')
            }
        })
        
        print("✅ Container configuré")
        
        # Créer le service de rapport
        report_service = container.report_service()
        print("✅ Service de rapport créé")
        
        # Générer le rapport
        print("📊 Génération du rapport avec les nouvelles modifications...")
        report_data = report_service.generate_report()
        
        print(f"✅ Rapport généré avec {len(report_data)} retailers")
        
        # Analyser les données pour vérifier les corrections
        print("\n📋 Analyse des données extraites:")
        print("=" * 60)
        
        success_count = 0
        warning_count = 0
        error_count = 0
        
        for i, retailer in enumerate(report_data[:5]):  # Afficher les 5 premiers
            name = retailer.get('name', 'N/A')
            crawling_rate = retailer.get('crawling_rate', 0)
            content_rate = retailer.get('content_rate', 0)
            crawling_status = retailer.get('crawling_status', 'N/A')
            content_status = retailer.get('content_status', 'N/A')
            final_status = retailer.get('final_status', 'N/A')
            
            print(f"\n🏪 {i+1}. {name}")
            print(f"   📊 Crawling: {crawling_rate}% ({crawling_status})")
            print(f"   📋 Content: {content_rate}% ({content_status})")
            print(f"   🎯 Statut final: {final_status}")
            
            # Compter les statuts
            if final_status == 'success':
                success_count += 1
            elif final_status == 'warning':
                warning_count += 1
            elif final_status == 'error':
                error_count += 1
        
        # Statistiques globales
        print(f"\n📈 Statistiques sur les {len(report_data)} retailers:")
        print(f"   ✅ Succès: {len([r for r in report_data if r.get('final_status') == 'success'])}")
        print(f"   ⚠️  Warning: {len([r for r in report_data if r.get('final_status') == 'warning'])}")
        print(f"   ❌ Erreur: {len([r for r in report_data if r.get('final_status') == 'error'])}")
        
        # Vérifier si les taux de succès sont réalistes (pas 0% partout)
        non_zero_rates = [r for r in report_data if r.get('crawling_rate', 0) > 0 or r.get('content_rate', 0) > 0]
        print(f"\n🔍 Retailers avec taux > 0%: {len(non_zero_rates)}/{len(report_data)}")
        
        if len(non_zero_rates) > 0:
            print("✅ Les modifications semblent fonctionner - taux non nuls détectés!")
        else:
            print("⚠️  Tous les taux sont à 0% - vérifier l'extraction")
        
        print("\n🎯 Test terminé!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
