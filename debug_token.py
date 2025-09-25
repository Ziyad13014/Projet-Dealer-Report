#!/usr/bin/env python3
"""Script pour déboguer et afficher le token JWT"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def show_token():
    try:
        from cli.services.auth import SpiderVisionAuth
        
        auth = SpiderVisionAuth()
        print(f"🔐 Tentative de connexion à: {auth.api_base}")
        print(f"📧 Email: {auth.email}")
        
        token = auth.login()
        
        print(f"\n✅ Token JWT obtenu:")
        print(f"📝 Token complet: {token}")
        print(f"📏 Longueur: {len(token)} caractères")
        print(f"🔍 Début: {token[:50]}...")
        print(f"🔍 Fin: ...{token[-50:]}")
        
        # Vérifier si c'est un JWT valide (format: header.payload.signature)
        parts = token.split('.')
        print(f"\n🧩 Parties du JWT: {len(parts)} (devrait être 3)")
        if len(parts) == 3:
            print("✅ Format JWT valide")
        else:
            print("⚠️ Format JWT inhabituel")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    show_token()
