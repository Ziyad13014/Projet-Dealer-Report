#!/usr/bin/env python3
"""Générer les données actuelles depuis l'API SpiderVision"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def generate_current_data():
    try:
        from cli.services.auth import SpiderVisionAuth
        from cli.services.data import SpiderVisionData
        from cli.services.export import DataExporter
        from cli.services.html_export import HTMLExporter
        
        print("🔐 Authentification...")
        auth = SpiderVisionAuth()
        token = auth.login()
        print("✅ Authentifié")
        
        print("📊 Récupération des données...")
        data_service = SpiderVisionData()
        overview_data = data_service.get_overview(token)
        print("✅ Données récupérées")
        
        print("💾 Export CSV...")
        exporter = DataExporter()
        csv_path = exporter.save_to_csv(overview_data, 'spider_vision_overview_current.csv')
        print(f"✅ CSV: {csv_path}")
        
        print("🌐 Export HTML avec filtres...")
        html_exporter = HTMLExporter()
        html_path = html_exporter.generate_html_report(overview_data, "reports/spider_vision_filtered_report.html")
        print(f"✅ HTML: {html_path}")
        
        print(f"\n🎉 Fichiers générés:")
        print(f"📄 CSV: {csv_path}")
        print(f"🌐 HTML: {html_path}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_current_data()
