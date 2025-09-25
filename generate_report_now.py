#!/usr/bin/env python3
"""Générer un rapport maintenant avec les modifications WebDataRepository"""

import os
import sys
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("🔄 Génération d'un rapport avec WebDataRepository corrigé...")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        # Charger l'environnement
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import des modules
        from cli.services.ReportService import ReportService
        from cli.repository.WebDataRepository import WebDataRepository
        from cli.ioc import Container
        
        # Configurer le container pour utiliser WebDataRepository
        container = Container()
        container.config.from_dict({
            'spider_vision': {
                'url': os.getenv('SPIDER_VISION_URL'),
                'username': os.getenv('SPIDER_VISION_USERNAME'),
                'password': os.getenv('SPIDER_VISION_PASSWORD')
            }
        })
        
        print("✅ Configuration chargée")
        
        # Créer le service de rapport
        report_service = container.report_service()
        print("✅ Service de rapport initialisé")
        
        # Générer le rapport
        print("📊 Génération du rapport en cours...")
        report_data = report_service.generate_report()
        
        print(f"✅ Rapport généré: {len(report_data)} retailers")
        
        # Analyser et afficher les résultats
        print("\n" + "="*70)
        print("📋 RÉSULTATS DU RAPPORT AVEC WEBDATAREPOSITORY CORRIGÉ")
        print("="*70)
        
        # Compter les statuts
        status_counts = {'success': 0, 'warning': 0, 'error': 0}
        
        # Afficher les premiers retailers avec détails
        print(f"\n🏪 DÉTAILS DES RETAILERS (5 premiers sur {len(report_data)}):")
        
        for i, retailer in enumerate(report_data[:5]):
            name = retailer.get('name', 'N/A')
            crawling_rate = retailer.get('crawling_rate', 0)
            content_rate = retailer.get('content_rate', 0)
            crawling_status = retailer.get('crawling_status', 'N/A')
            content_status = retailer.get('content_status', 'N/A')
            final_status = retailer.get('final_status', 'N/A')
            
            # Icônes selon le statut
            status_icon = {'success': '✅', 'warning': '⚠️', 'error': '❌'}.get(final_status, '❓')
            
            print(f"\n{i+1}. {status_icon} {name}")
            print(f"   📊 Crawling: {crawling_rate}% → {crawling_status}")
            print(f"   📋 Content: {content_rate}% → {content_status}")
            print(f"   🎯 Final: {final_status}")
            
            if final_status in status_counts:
                status_counts[final_status] += 1
        
        # Compter tous les statuts
        for retailer in report_data:
            final_status = retailer.get('final_status', 'unknown')
            if final_status in status_counts:
                status_counts[final_status] += 1
        
        # Statistiques globales
        print(f"\n📈 STATISTIQUES GLOBALES:")
        print(f"   ✅ Succès: {status_counts['success']} retailers")
        print(f"   ⚠️  Warning: {status_counts['warning']} retailers") 
        print(f"   ❌ Erreur: {status_counts['error']} retailers")
        print(f"   📊 Total: {len(report_data)} retailers")
        
        # Vérifier la qualité des données
        non_zero_crawling = len([r for r in report_data if r.get('crawling_rate', 0) > 0])
        non_zero_content = len([r for r in report_data if r.get('content_rate', 0) > 0])
        
        print(f"\n🔍 QUALITÉ DES DONNÉES:")
        print(f"   📊 Retailers avec crawling_rate > 0%: {non_zero_crawling}/{len(report_data)}")
        print(f"   📋 Retailers avec content_rate > 0%: {non_zero_content}/{len(report_data)}")
        
        if non_zero_crawling > 0 or non_zero_content > 0:
            print("   ✅ Extraction des pourcentages fonctionne!")
        else:
            print("   ⚠️  Tous les taux sont à 0% - vérifier l'extraction")
        
        # Exemples de taux élevés
        high_performers = [r for r in report_data if r.get('crawling_rate', 0) > 90]
        if high_performers:
            print(f"\n🌟 PERFORMERS (crawling > 90%): {len(high_performers)} retailers")
            for perf in high_performers[:3]:
                print(f"   • {perf.get('name', 'N/A')}: {perf.get('crawling_rate', 0)}%")
        
        print(f"\n🎯 Rapport terminé à {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
