#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script autonome pour récupérer le vrai token SpiderVision via Playwright.
Compatible avec GitHub Actions (mode headless).
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright n'est pas installé.")
    print("Installez-le avec: pip install playwright && playwright install chromium")
    sys.exit(1)


def load_cached_token():
    """Charge le token depuis le cache s'il existe et est encore valide (< 1h)."""
    token_file = Path(".spidervision_token.json")
    if not token_file.exists():
        return None
    
    try:
        with open(token_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        token = data.get('token')
        timestamp = data.get('timestamp', 0)
        
        age_seconds = time.time() - timestamp
        if age_seconds < 3600 and token:
            print(f"✅ Token en cache trouvé (âge: {int(age_seconds)}s)")
            return token
    except Exception as e:
        print(f"⚠️ Erreur lecture cache: {e}")
    
    return None


def save_token(token):
    """Sauvegarde le token dans un fichier JSON avec timestamp."""
    token_file = Path(".spidervision_token.json")
    data = {
        "token": token,
        "timestamp": int(time.time())
    }
    
    try:
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Token sauvegardé dans {token_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False


def get_spidervision_token(email, password):
    """Récupère le vrai token SpiderVision en simulant une connexion navigateur."""
    print("🚀 Connexion à SpiderVision...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)  # Mode visible pour debug
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            login_url = "https://spider-vision.data-solutions.com/#/"
            print(f"📍 Navigation vers {login_url}")
            page.goto(login_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # Essayer différents sélecteurs possibles
            print("🔍 Recherche du formulaire de login...")
            selectors_email = [
                "input[type='email']",
                "input[name='email']",
                "input[id='email']",
                "input[placeholder*='email' i]",
                "input[placeholder*='Email' i]"
            ]
            
            email_field = None
            for selector in selectors_email:
                try:
                    email_field = page.wait_for_selector(selector, timeout=2000)
                    if email_field:
                        print(f"✅ Champ email trouvé: {selector}")
                        break
                except:
                    continue
            
            if not email_field:
                print("❌ Champ email introuvable")
                print("📸 Sauvegarde screenshot...")
                page.screenshot(path="debug_login.png")
                browser.close()
                return None
            
            # Remplir le formulaire
            page.fill(selector, email)
            time.sleep(0.5)
            
            # Chercher le champ password
            selectors_password = [
                "input[type='password']",
                "input[name='password']",
                "input[id='password']"
            ]
            
            for selector_pwd in selectors_password:
                try:
                    page.fill(selector_pwd, password)
                    print(f"✅ Champ password trouvé: {selector_pwd}")
                    break
                except:
                    continue
            
            time.sleep(0.5)
            
            # Cliquer sur le bouton de connexion
            page.click("button[type='submit']")
            print("🔄 Authentification en cours...")
            time.sleep(5)
            
            # Récupérer le token depuis localStorage
            print("🔍 Recherche du token dans localStorage...")
            token_keys = ['auth_token', 'token', 'jwt', 'access_token', 'authToken']
            token = None
            
            for key in token_keys:
                token = page.evaluate(f"() => window.localStorage.getItem('{key}')")
                if token:
                    print(f"✅ Token trouvé dans localStorage['{key}']")
                    break
            
            if not token:
                print("⚠️ Token non trouvé dans localStorage, essai cookies...")
                cookies = context.cookies()
                for cookie in cookies:
                    if cookie['name'] in token_keys:
                        token = cookie['value']
                        print(f"✅ Token trouvé dans cookie '{cookie['name']}'")
                        break
            
            browser.close()
            
            if not token:
                print("❌ Impossible de récupérer le token")
                return None
            
            print("✅ Token récupéré avec succès.")
            return token
            
        except PlaywrightTimeout as e:
            print(f"❌ Timeout: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du token: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Fonction principale."""
    email = "crawl@wiser.com"
    password = "cra@01012024?"
    
    cached_token = load_cached_token()
    if cached_token:
        print("\n=== TOKEN SPIDERVISION (CACHE) ===")
        print(cached_token)
        print("==================================\n")
        return 0
    
    token = get_spidervision_token(email, password)
    
    if not token:
        print("\n❌ Échec de la récupération du token.")
        return 1
    
    print("\n=== TOKEN SPIDERVISION ===")
    print(token)
    print("==========================\n")
    
    save_token(token)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
