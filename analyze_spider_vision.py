#!/usr/bin/env python3
"""Script pour analyser l'API Spider Vision et découvrir les endpoints réels."""

import requests
import json
import re
from urllib.parse import urljoin
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpiderVisionAnalyzer:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_main_page(self):
        """Analyser la page principale pour découvrir l'architecture."""
        print("🔍 Analyse de la page principale...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            
            content = response.text
            print(f"✅ Page principale récupérée ({len(content)} caractères)")
            
            # Chercher des indices sur l'API
            api_patterns = [
                r'/api/[a-zA-Z0-9/_-]+',
                r'fetch\(["\']([^"\']+)["\']',
                r'axios\.[a-z]+\(["\']([^"\']+)["\']',
                r'\.post\(["\']([^"\']+)["\']',
                r'\.get\(["\']([^"\']+)["\']',
                r'endpoint["\']?\s*:\s*["\']([^"\']+)["\']',
                r'url["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            found_endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.startswith('/') or match.startswith('http'):
                        found_endpoints.add(match)
            
            if found_endpoints:
                print(f"📋 Endpoints potentiels trouvés:")
                for endpoint in sorted(found_endpoints):
                    print(f"  - {endpoint}")
            else:
                print("⚠️ Aucun endpoint API évident trouvé dans le HTML")
            
            # Chercher des scripts JS
            js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', content)
            if js_files:
                print(f"\n📜 Fichiers JavaScript trouvés:")
                for js_file in js_files[:5]:  # Limiter à 5
                    print(f"  - {js_file}")
                    
            return found_endpoints, js_files
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            return set(), []
    
    def test_common_endpoints(self):
        """Tester des endpoints communs pour les applications React/SPA."""
        print("\n🧪 Test d'endpoints communs...")
        
        common_endpoints = [
            '/api',
            '/api/v1',
            '/api/auth',
            '/api/user',
            '/api/login',
            '/auth',
            '/login',
            '/signin',
            '/session',
            '/api/session',
            '/graphql',
            '/api/graphql'
        ]
        
        working_endpoints = []
        
        for endpoint in common_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code != 404:
                    status_info = f"HTTP {response.status_code}"
                    if response.headers.get('content-type', '').startswith('application/json'):
                        try:
                            data = response.json()
                            status_info += f" (JSON: {len(str(data))} chars)"
                        except:
                            pass
                    
                    print(f"✅ {endpoint} -> {status_info}")
                    working_endpoints.append((endpoint, response.status_code))
                else:
                    print(f"❌ {endpoint} -> 404")
                    
            except Exception as e:
                print(f"⚠️ {endpoint} -> Erreur: {e}")
        
        return working_endpoints
    
    def analyze_network_requests(self):
        """Simuler une session utilisateur pour voir les requêtes réseau."""
        print("\n🌐 Analyse des requêtes réseau simulées...")
        
        # Essayer de charger la page et voir si elle fait des requêtes AJAX
        try:
            # Première requête pour obtenir la page
            response = self.session.get(f"{self.base_url}/")
            
            # Chercher des tokens CSRF ou autres dans les cookies/headers
            cookies = self.session.cookies.get_dict()
            if cookies:
                print(f"🍪 Cookies reçus: {list(cookies.keys())}")
            
            # Essayer des requêtes qui pourraient être faites par l'app
            potential_requests = [
                ('/api/me', 'GET'),
                ('/api/user/profile', 'GET'),
                ('/api/dashboard', 'GET'),
                ('/api/status', 'GET'),
                ('/api/health', 'GET'),
                ('/api/config', 'GET')
            ]
            
            for endpoint, method in potential_requests:
                try:
                    if method == 'GET':
                        resp = self.session.get(f"{self.base_url}{endpoint}")
                    else:
                        resp = self.session.post(f"{self.base_url}{endpoint}")
                    
                    if resp.status_code not in [404, 405]:
                        print(f"✅ {method} {endpoint} -> HTTP {resp.status_code}")
                        if resp.headers.get('content-type', '').startswith('application/json'):
                            try:
                                data = resp.json()
                                print(f"   📄 Réponse JSON: {json.dumps(data, indent=2)[:200]}...")
                            except:
                                pass
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse réseau: {e}")
    
    def try_authentication_methods(self):
        """Essayer différentes méthodes d'authentification."""
        print("\n🔐 Test de méthodes d'authentification alternatives...")
        
        # Méthode 1: Form-based authentication (comme les sites web classiques)
        try:
            # Chercher un formulaire de login
            response = self.session.get(f"{self.base_url}/")
            if 'login' in response.text.lower() or 'signin' in response.text.lower():
                print("✅ Indices de formulaire de login trouvés dans la page")
                
                # Essayer de poster directement sur la racine
                login_data = {
                    'username': self.username,
                    'password': self.password,
                    'email': self.username,
                    'login': self.username
                }
                
                response = self.session.post(f"{self.base_url}/", data=login_data)
                print(f"📤 POST / -> HTTP {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Erreur méthode form: {e}")
        
        # Méthode 2: Essayer avec des headers d'authentification
        try:
            import base64
            auth_string = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers = {'Authorization': f'Basic {auth_string}'}
            
            response = self.session.get(f"{self.base_url}/api", headers=headers)
            if response.status_code != 404:
                print(f"✅ Basic Auth sur /api -> HTTP {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Erreur Basic Auth: {e}")

def main():
    print("🕷️ ANALYSEUR SPIDER VISION")
    print("=" * 50)
    
    # Credentials
    base_url = "https://spider-vision.data-solutions.com"
    username = "crawl@wiser.com"
    password = "cra@01012024?"
    
    analyzer = SpiderVisionAnalyzer(base_url, username, password)
    
    # 1. Analyser la page principale
    endpoints, js_files = analyzer.analyze_main_page()
    
    # 2. Tester des endpoints communs
    working_endpoints = analyzer.test_common_endpoints()
    
    # 3. Analyser les requêtes réseau
    analyzer.analyze_network_requests()
    
    # 4. Tester l'authentification
    analyzer.try_authentication_methods()
    
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DE L'ANALYSE")
    print(f"Endpoints fonctionnels: {len(working_endpoints)}")
    for endpoint, status in working_endpoints:
        print(f"  - {endpoint} (HTTP {status})")
    
    if not working_endpoints:
        print("⚠️ Aucun endpoint API trouvé. Le site utilise probablement:")
        print("  - Une SPA (Single Page Application) avec authentification côté client")
        print("  - Des WebSockets ou Server-Sent Events")
        print("  - Une API GraphQL")
        print("  - Une authentification par cookies/session")

if __name__ == "__main__":
    main()
