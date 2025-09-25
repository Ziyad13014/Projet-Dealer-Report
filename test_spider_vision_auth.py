#!/usr/bin/env python3
"""Script de test pour l'authentification Spider Vision."""

import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_spider_vision_connection():
    """Tester la connexion à Spider Vision."""
    
    base_url = os.getenv('SPIDER_VISION_URL', 'https://spider-vision.data-solutions.com/')
    username = os.getenv('SPIDER_VISION_USERNAME', 'crawl@wiser.com')
    password = os.getenv('SPIDER_VISION_PASSWORD', 'cra@01012024?')
    
    print(f"🔍 Test de connexion à Spider Vision")
    print(f"URL: {base_url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print("-" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # Test 1: Accès à la page principale
        print("📡 Test 1: Accès à la page principale...")
        response = session.get(base_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content preview: {response.text[:200]}...")
        print()
        
        # Test 2: Tentatives de login
        login_endpoints = ['/api/auth/login', '/login', '/api/login', '/auth/login']
        login_data = {'username': username, 'password': password}
        
        for endpoint in login_endpoints:
            print(f"🔐 Test login via {endpoint}...")
            try:
                # Test JSON
                resp = session.post(f"{base_url.rstrip('/')}{endpoint}", 
                                  json=login_data, timeout=10)
                print(f"  JSON - Status: {resp.status_code}, Content: {resp.text[:100]}")
                
                # Test Form data
                resp = session.post(f"{base_url.rstrip('/')}{endpoint}", 
                                  data=login_data, timeout=10)
                print(f"  FORM - Status: {resp.status_code}, Content: {resp.text[:100]}")
                
            except Exception as e:
                print(f"  Erreur: {e}")
            print()
        
        # Test 3: Recherche d'API endpoints
        api_endpoints = ['/api/', '/api/status', '/api/health', '/api/retailers', '/api/crawler']
        
        for endpoint in api_endpoints:
            print(f"🔍 Test endpoint {endpoint}...")
            try:
                resp = session.get(f"{base_url.rstrip('/')}{endpoint}", timeout=5)
                print(f"  Status: {resp.status_code}, Content: {resp.text[:100]}")
            except Exception as e:
                print(f"  Erreur: {e}")
            print()
                
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_spider_vision_connection()
