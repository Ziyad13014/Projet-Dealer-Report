#!/usr/bin/env python3
"""Test de génération du rapport HTML"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def test_html_generation():
    try:
        # Lire les données CSV existantes
        csv_path = "reports/spider_vision_overview_20250909_103512.csv"
        if not os.path.exists(csv_path):
            print("❌ Fichier CSV non trouvé")
            return
        
        # Charger les données CSV
        df = pd.read_csv(csv_path)
        data = df.to_dict('records')
        
        print(f"✅ Données CSV chargées: {len(data)} retailers")
        
        # Générer le rapport HTML
        from cli.services.html_export import HTMLExporter
        
        html_exporter = HTMLExporter()
        html_path = html_exporter.generate_html_report(data, "reports/test_spider_vision_report.html")
        
        print(f"✅ Rapport HTML généré: {html_path}")
        
        # Vérifier que le fichier existe
        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"✅ Fichier HTML créé ({file_size} bytes)")
            print(f"🌐 Ouvrez le fichier dans votre navigateur: {os.path.abspath(html_path)}")
        else:
            print("❌ Fichier HTML non créé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_generation()
