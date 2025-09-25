#!/usr/bin/env python3
"""Script pour analyser le bundle JavaScript de Spider Vision."""

import requests
import re
import json
from urllib.parse import urljoin

def analyze_js_bundle():
    """Analyser le bundle JavaScript pour trouver les endpoints API."""
    print("📜 ANALYSE DU BUNDLE JAVASCRIPT")
    print("=" * 50)
    
    bundle_url = "https://spider-vision.data-solutions.com/6cb7fb1fbe68b7723c7d.bundle.js"
    
    try:
        print("📥 Téléchargement du bundle JavaScript...")
        response = requests.get(bundle_url)
        response.raise_for_status()
        
        js_content = response.text
        print(f"✅ Bundle téléchargé ({len(js_content)} caractères)")
        
        # Patterns pour trouver les endpoints API
        patterns = {
            'endpoints': [
                r'["\']/(api/[^"\']+)["\']',
                r'["\']([^"\']*api[^"\']*)["\']',
                r'endpoint["\']?\s*:\s*["\']([^"\']+)["\']',
                r'url["\']?\s*:\s*["\']([^"\']+)["\']',
                r'baseURL["\']?\s*:\s*["\']([^"\']+)["\']',
                r'fetch\(["\']([^"\']+)["\']',
                r'axios\.[a-z]+\(["\']([^"\']+)["\']',
                r'\.post\(["\']([^"\']+)["\']',
                r'\.get\(["\']([^"\']+)["\']',
                r'\.put\(["\']([^"\']+)["\']',
                r'\.delete\(["\']([^"\']+)["\']'
            ],
            'auth_patterns': [
                r'login["\']?\s*:\s*["\']([^"\']+)["\']',
                r'auth["\']?\s*:\s*["\']([^"\']+)["\']',
                r'signin["\']?\s*:\s*["\']([^"\']+)["\']',
                r'token["\']?\s*:\s*["\']([^"\']+)["\']',
                r'jwt["\']?\s*:\s*["\']([^"\']+)["\']'
            ],
            'data_patterns': [
                r'crawler["\']?\s*:\s*["\']([^"\']+)["\']',
                r'spider["\']?\s*:\s*["\']([^"\']+)["\']',
                r'data["\']?\s*:\s*["\']([^"\']+)["\']',
                r'stats["\']?\s*:\s*["\']([^"\']+)["\']',
                r'report["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
        }
        
        found_items = {}
        
        for category, pattern_list in patterns.items():
            found_items[category] = set()
            for pattern in pattern_list:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if match and (match.startswith('/') or match.startswith('http') or 'api' in match.lower()):
                        found_items[category].add(match)
        
        # Afficher les résultats
        print("\n🔍 ENDPOINTS TROUVÉS:")
        if found_items['endpoints']:
            for endpoint in sorted(found_items['endpoints']):
                print(f"  - {endpoint}")
        else:
            print("  ❌ Aucun endpoint trouvé")
        
        print("\n🔐 PATTERNS D'AUTHENTIFICATION:")
        if found_items['auth_patterns']:
            for auth in sorted(found_items['auth_patterns']):
                print(f"  - {auth}")
        else:
            print("  ❌ Aucun pattern d'auth trouvé")
        
        print("\n📊 PATTERNS DE DONNÉES:")
        if found_items['data_patterns']:
            for data in sorted(found_items['data_patterns']):
                print(f"  - {data}")
        else:
            print("  ❌ Aucun pattern de données trouvé")
        
        # Chercher des configurations spécifiques
        print("\n⚙️ CONFIGURATIONS TROUVÉES:")
        config_patterns = [
            r'baseURL["\']?\s*:\s*["\']([^"\']+)["\']',
            r'apiUrl["\']?\s*:\s*["\']([^"\']+)["\']',
            r'serverUrl["\']?\s*:\s*["\']([^"\']+)["\']',
            r'backendUrl["\']?\s*:\s*["\']([^"\']+)["\']'
        ]
        
        configs = set()
        for pattern in config_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            configs.update(matches)
        
        if configs:
            for config in sorted(configs):
                print(f"  - {config}")
        else:
            print("  ❌ Aucune configuration d'URL trouvée")
        
        # Chercher des WebSocket ou autres protocoles
        print("\n🌐 AUTRES PROTOCOLES:")
        ws_patterns = [
            r'ws://[^"\']+',
            r'wss://[^"\']+',
            r'socket\.io[^"\']*',
            r'websocket[^"\']*'
        ]
        
        other_protocols = set()
        for pattern in ws_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            other_protocols.update(matches)
        
        if other_protocols:
            for protocol in sorted(other_protocols):
                print(f"  - {protocol}")
        else:
            print("  ❌ Aucun autre protocole trouvé")
        
        return found_items
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return {}

def test_discovered_endpoints(found_items):
    """Tester les endpoints découverts."""
    print("\n🧪 TEST DES ENDPOINTS DÉCOUVERTS")
    print("=" * 40)
    
    base_url = "https://spider-vision.data-solutions.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    endpoints_to_test = found_items.get('endpoints', set())
    
    if not endpoints_to_test:
        print("❌ Aucun endpoint à tester")
        return
    
    working_endpoints = []
    
    for endpoint in sorted(endpoints_to_test)[:10]:  # Limiter à 10 tests
        try:
            if not endpoint.startswith('http'):
                if not endpoint.startswith('/'):
                    endpoint = '/' + endpoint
                test_url = base_url + endpoint
            else:
                test_url = endpoint
            
            response = session.get(test_url, timeout=5)
            
            if response.status_code != 404:
                status_info = f"HTTP {response.status_code}"
                if response.headers.get('content-type', '').startswith('application/json'):
                    status_info += " (JSON)"
                
                print(f"✅ {endpoint} -> {status_info}")
                working_endpoints.append((endpoint, response.status_code))
            else:
                print(f"❌ {endpoint} -> 404")
                
        except Exception as e:
            print(f"⚠️ {endpoint} -> Erreur: {str(e)[:50]}")
    
    return working_endpoints

def main():
    found_items = analyze_js_bundle()
    
    if found_items:
        working_endpoints = test_discovered_endpoints(found_items)
        
        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ")
        
        total_found = sum(len(items) for items in found_items.values())
        print(f"Total d'éléments trouvés: {total_found}")
        
        if working_endpoints:
            print(f"Endpoints fonctionnels: {len(working_endpoints)}")
            for endpoint, status in working_endpoints:
                print(f"  - {endpoint} (HTTP {status})")
        else:
            print("❌ Aucun endpoint fonctionnel trouvé")
            print("\n💡 RECOMMANDATIONS:")
            print("1. Le site utilise probablement une authentification par session/cookies")
            print("2. Les données sont peut-être chargées dynamiquement via JavaScript")
            print("3. Il pourrait y avoir une API GraphQL ou des WebSockets")
            print("4. Considérer l'utilisation de Selenium pour automatiser le navigateur")

if __name__ == "__main__":
    main()
