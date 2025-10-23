#!/usr/bin/env python3
"""Test de connexion et analyse de SpiderVision"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

def test_spider_vision():
    # 1. Authentification
    print("=" * 60)
    print("TEST 1: AUTHENTIFICATION")
    print("=" * 60)
    
    try:
        from cli.services.auth import SpiderVisionAuth
        auth = SpiderVisionAuth()
        token = auth.login()
        print(f"✅ Authentification réussie")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # 2. Analyse de la page
    print("\n" + "=" * 60)
    print("TEST 2: ANALYSE DE LA PAGE")
    print("=" * 60)
    
    page_url = 'https://spider-vision.data-solutions.com'
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Mozilla/5.0'
    }
    
    response = requests.get(page_url, headers=headers, timeout=30)
    print(f"✅ Status: {response.status_code}")
    
    # Sauvegarder le HTML
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"📄 HTML sauvegardé: debug_page.html")
    
    # Parser
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    print(f"📊 Tableaux trouvés: {len(tables)}")
    
    scripts = soup.find_all('script')
    print(f"📜 Scripts trouvés: {len(scripts)}")
    
    # Chercher React/Vue
    root = soup.find(id='root') or soup.find(id='app')
    if root:
        print(f"⚛️ App React/Vue détectée")
    
    print("\n💡 Consultez debug_page.html pour plus de détails")

if __name__ == "__main__":
    test_spider_vision()