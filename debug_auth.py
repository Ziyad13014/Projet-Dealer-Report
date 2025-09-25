#!/usr/bin/env python3
"""Script de diagnostic détaillé pour l'authentification Spider Vision."""

import requests
import os
from dotenv import load_dotenv
import logging

# Configuration du logging détaillé
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

def debug_spider_vision_auth():
    """Diagnostic détaillé de l'authentification Spider Vision"""
    
    base_url = os.getenv('SPIDER_VISION_URL', 'https://spider-vision.data-solutions.com')
    username = os.getenv('SPIDER_VISION_USERNAME', 'crawl@wiser.com')
    password = os.getenv('SPIDER_VISION_PASSWORD', 'cra@01012024?')
    
    print("🔍 Diagnostic détaillé de l'authentification Spider Vision")
    print(f"URL: {base_url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print("=" * 70)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        # Test 1: Accès à la page principale
        print("\n📡 Test 1: Accès à la page principale...")
        try:
            response = session.get(base_url, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"URL finale après redirections: {response.url}")
            print(f"Contenu (200 premiers caractères): {response.text[:200]}")
            
            if response.status_code != 200:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            return
        
        # Test 2: Analyser le contenu HTML pour trouver le formulaire de login
        print("\n🔍 Test 2: Analyse du contenu HTML...")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Chercher les formulaires
        forms = soup.find_all('form')
        print(f"Nombre de formulaires trouvés: {len(forms)}")
        
        for i, form in enumerate(forms):
            print(f"  Formulaire {i+1}:")
            print(f"    Action: {form.get('action', 'Non définie')}")
            print(f"    Method: {form.get('method', 'GET')}")
            inputs = form.find_all('input')
            for inp in inputs:
                print(f"    Input: name='{inp.get('name')}', type='{inp.get('type')}', id='{inp.get('id')}'")
        
        # Chercher des indices d'une SPA (Single Page Application)
        scripts = soup.find_all('script')
        print(f"\nNombre de scripts trouvés: {len(scripts)}")
        
        spa_indicators = ['angular', 'react', 'vue', 'app.js', 'main.js', 'bundle.js']
        for script in scripts:
            src = script.get('src', '')
            if any(indicator in src.lower() for indicator in spa_indicators):
                print(f"  SPA détectée: {src}")
        
        # Test 3: Tentatives d'authentification
        print("\n🔐 Test 3: Tentatives d'authentification...")
        
        login_data = {
            'username': username,
            'password': password,
            'email': username,  # Parfois c'est email au lieu de username
            'login': username,
            'user': username
        }
        
        # Endpoints à tester
        login_endpoints = [
            '/api/auth/login',
            '/api/login', 
            '/login',
            '/auth/login',
            '/api/authenticate',
            '/authenticate',
            '/api/session',
            '/session'
        ]
        
        for endpoint in login_endpoints:
            print(f"\n  🔑 Test endpoint: {endpoint}")
            
            # Test POST JSON
            try:
                url = f"{base_url.rstrip('/')}{endpoint}"
                resp = session.post(url, json=login_data, timeout=10)
                print(f"    JSON - Status: {resp.status_code}")
                print(f"    JSON - Headers: {dict(resp.headers)}")
                print(f"    JSON - Content: {resp.text[:200]}")
                
                if resp.status_code == 200 and 'error' not in resp.text.lower():
                    print(f"    ✅ Succès potentiel avec {endpoint} (JSON)")
                    
            except Exception as e:
                print(f"    JSON - Erreur: {e}")
            
            # Test POST Form data
            try:
                resp = session.post(url, data=login_data, timeout=10)
                print(f"    FORM - Status: {resp.status_code}")
                print(f"    FORM - Content: {resp.text[:200]}")
                
                if resp.status_code == 200 and 'error' not in resp.text.lower():
                    print(f"    ✅ Succès potentiel avec {endpoint} (FORM)")
                    
            except Exception as e:
                print(f"    FORM - Erreur: {e}")
        
        # Test 4: Vérifier les cookies et sessions
        print(f"\n🍪 Test 4: Cookies de session...")
        print(f"Cookies actuels: {dict(session.cookies)}")
        
        # Test 5: Essayer d'accéder à des pages protégées
        print(f"\n🔒 Test 5: Test d'accès aux pages protégées...")
        protected_endpoints = [
            '/dashboard',
            '/api/dashboard',
            '/api/retailers',
            '/api/data',
            '/home',
            '/main'
        ]
        
        for endpoint in protected_endpoints:
            try:
                url = f"{base_url.rstrip('/')}{endpoint}"
                resp = session.get(url, timeout=10)
                print(f"  {endpoint}: Status {resp.status_code}, Content: {resp.text[:100]}")
            except Exception as e:
                print(f"  {endpoint}: Erreur {e}")
                
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_spider_vision_auth()
