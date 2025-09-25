#!/usr/bin/env python3
"""Test simple pour générer un rapport"""

from datetime import datetime
import os

def test_simple_report():
    """Test de génération de rapport simple"""
    print("🔄 Test de génération de rapport...")
    
    # Créer le dossier reports s'il n'existe pas
    os.makedirs('reports', exist_ok=True)
    
    # Générer un rapport simple
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'reports/test_report_{timestamp}.html'
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Test Rapport - {datetime.now().strftime("%d/%m/%Y à %H:%M")}</title>
</head>
<body>
    <h1>🧪 Test Rapport SpiderVision</h1>
    <p>Généré le: {datetime.now().strftime("%d/%m/%Y à %H:%M")}</p>
    <p>✅ Le système fonctionne correctement!</p>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Test réussi: {output_file}")
    return output_file

if __name__ == "__main__":
    test_simple_report()
