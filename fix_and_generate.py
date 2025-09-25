#!/usr/bin/env python3
"""Script pour corriger et générer le rapport HTML avec filtres"""

import os
import sys
import json
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("🔧 Correction et génération du rapport HTML avec filtres...")
        
        # Importer les modules nécessaires
        from dotenv import load_dotenv
        load_dotenv()
        
        from cli.services.auth import SpiderVisionAuth
        from cli.services.data import SpiderVisionData
        from cli.services.export import DataExporter
        from cli.services.html_export import HTMLExporter
        
        # Étape 1: Authentification
        print("🔐 Authentification...")
        auth = SpiderVisionAuth()
        token = auth.login()
        print("✅ Authentification réussie")
        
        # Étape 2: Récupération des données
        print("📊 Récupération des données overview...")
        data_service = SpiderVisionData()
        overview_data = data_service.get_overview(token)
        print(f"✅ Données récupérées ({len(str(overview_data))} caractères)")
        
        # Étape 3: Export CSV
        print("💾 Génération du fichier CSV...")
        exporter = DataExporter()
        csv_path = exporter.save_to_csv(overview_data, 'spider_vision_overview_current.csv')
        print(f"✅ CSV généré: {csv_path}")
        
        # Étape 4: Export HTML avec filtres
        print("🌐 Génération du rapport HTML avec filtres...")
        html_exporter = HTMLExporter()
        html_path = html_exporter.generate_html_report(overview_data, "reports/spider_vision_filtered_report.html")
        print(f"✅ HTML généré: {html_path}")
        
        # Vérifier les fichiers
        if os.path.exists(csv_path):
            csv_size = os.path.getsize(csv_path)
            print(f"📄 CSV: {csv_path} ({csv_size} bytes)")
        
        if os.path.exists(html_path):
            html_size = os.path.getsize(html_path)
            print(f"🌐 HTML: {html_path} ({html_size} bytes)")
            
            # Chemin pour ouvrir dans le navigateur
            abs_html_path = os.path.abspath(html_path).replace('\\', '/')
            print(f"🔗 Ouvrir dans le navigateur: file:///{abs_html_path}")
        
        print("\n🎉 Génération terminée avec succès!")
        print("📋 Le rapport HTML contient maintenant:")
        print("   • 3 boutons de filtrage (Succès, Warning, Erreur)")
        print("   • Sélection multiple des filtres")
        print("   • Tri automatique par ordre de réussite")
        print("   • Statistiques dynamiques")
        print("   • Interface interactive")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
