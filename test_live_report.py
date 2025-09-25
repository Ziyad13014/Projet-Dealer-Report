#!/usr/bin/env python3
"""
Test script pour générer un rapport avec les vraies données API
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_api_connection():
    """Test de connexion à l'API SpiderVision"""
    
    # Configuration API
    api_base = os.getenv('SPIDER_VISION_API_BASE', 'https://food-api-spider-vision.data-solutions.com')
    jwt_token = os.getenv('SPIDER_VISION_JWT_TOKEN')
    overview_endpoint = os.getenv('SPIDER_VISION_OVERVIEW_ENDPOINT', '/store-history/overview')
    
    if not jwt_token:
        print("❌ Token JWT manquant dans .env")
        return None
    
    print(f"🔗 Test connexion API: {api_base}{overview_endpoint}")
    
    # Headers avec authentification
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        # Appel API
        response = requests.get(f"{api_base}{overview_endpoint}", headers=headers, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API OK - {len(data)} retailers trouvés")
            
            # Afficher quelques exemples
            for i, retailer in enumerate(data[:3]):
                name = retailer.get('retailer_name', 'Unknown')
                print(f"   {i+1}. {name}")
            
            return data
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur connexion: {e}")
        return None

def generate_real_report():
    """Génère un rapport avec les vraies données"""
    
    # Test API
    data = test_api_connection()
    if not data:
        print("❌ Impossible de récupérer les données API")
        return
    
    print(f"\n🎯 Génération du rapport avec {len(data)} retailers...")
    
    # Import des fonctions du script principal
    try:
        from generate_last_day_report import process_retailer_data, create_progress_bar, get_worst_status
        print("✅ Fonctions importées")
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return
    
    # Traitement des données
    processed_data = []
    for retailer_data in data:
        try:
            processed = process_retailer_data(retailer_data)
            processed_data.append(processed)
        except Exception as e:
            print(f"⚠️ Erreur traitement {retailer_data.get('retailer_name', 'Unknown')}: {e}")
    
    print(f"✅ {len(processed_data)} retailers traités")
    
    # Génération HTML simple
    current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport SpiderVision Live - {current_time}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .success {{ color: green; font-weight: bold; }}
        .warning {{ color: orange; font-weight: bold; }}
        .error {{ color: red; font-weight: bold; }}
        .error-critical {{ color: darkred; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📊 Rapport SpiderVision Live</h1>
    <p>Généré le {current_time} avec {len(processed_data)} retailers</p>
    
    <table>
        <thead>
            <tr>
                <th>Enseigne</th>
                <th>Progress (%)</th>
                <th>Statut Progress</th>
                <th>Success (%)</th>
                <th>Statut Success</th>
                <th>Statut Global</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for retailer in processed_data:
        status_class = retailer['global_status'].lower().replace('!', '-critical')
        html_content += f"""
            <tr>
                <td><strong>{retailer['retailer_name']}</strong></td>
                <td>{retailer['progress_avg']:.1f}%</td>
                <td class="{retailer['progress_status'].lower().replace('!', '-critical')}">{retailer['progress_status']}</td>
                <td>{retailer['success_avg']:.1f}%</td>
                <td class="{retailer['success_status'].lower().replace('!', '-critical')}">{retailer['success_status']}</td>
                <td class="{status_class}">{retailer['global_status']}</td>
            </tr>"""
    
    html_content += """
        </tbody>
    </table>
</body>
</html>"""
    
    # Sauvegarde
    filename = f"reports/live_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Rapport sauvegardé: {filename}")
    return filename

if __name__ == "__main__":
    print("🚀 Test génération rapport live SpiderVision\n")
    generate_real_report()
