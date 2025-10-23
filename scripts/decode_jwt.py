#!/usr/bin/env python3
"""Script pour décoder un token JWT et voir son contenu"""

import base64
import json

def decode_jwt(token):
    """Décode un token JWT pour voir son contenu"""
    try:
        # Un JWT a 3 parties séparées par des points
        parts = token.split('.')
        
        if len(parts) != 3:
            print("❌ Ce n'est pas un token JWT valide (doit avoir 3 parties)")
            return
        
        # Décoder la partie header (partie 1)
        header = parts[0]
        # Ajouter le padding si nécessaire
        header += '=' * (4 - len(header) % 4)
        header_decoded = base64.urlsafe_b64decode(header)
        header_json = json.loads(header_decoded)
        
        # Décoder la partie payload (partie 2)
        payload = parts[1]
        payload += '=' * (4 - len(payload) % 4)
        payload_decoded = base64.urlsafe_b64decode(payload)
        payload_json = json.loads(payload_decoded)
        
        print("=" * 80)
        print("🔍 ANALYSE DU TOKEN JWT")
        print("=" * 80)
        
        print("\n📋 HEADER:")
        print(json.dumps(header_json, indent=2))
        
        print("\n📦 PAYLOAD (données utilisateur):")
        print(json.dumps(payload_json, indent=2))
        
        # Analyser les informations importantes
        print("\n" + "=" * 80)
        print("📊 INFORMATIONS IMPORTANTES:")
        print("=" * 80)
        
        if 'sub' in payload_json:
            print(f"👤 User ID: {payload_json['sub']}")
        
        if 'email' in payload_json:
            print(f"📧 Email: {payload_json['email']}")
        
        if 'roles' in payload_json:
            print(f"🔑 Rôles: {payload_json['roles']}")
        
        if 'iat' in payload_json:
            from datetime import datetime
            iat = datetime.fromtimestamp(payload_json['iat'])
            print(f"📅 Créé le: {iat}")
        
        if 'exp' in payload_json:
            from datetime import datetime
            exp = datetime.fromtimestamp(payload_json['exp'])
            now = datetime.now()
            print(f"⏰ Expire le: {exp}")
            if exp < now:
                print(f"   ❌ Token EXPIRÉ depuis {now - exp}")
            else:
                print(f"   ✅ Token valide encore {exp - now}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erreur lors du décodage: {e}")

if __name__ == "__main__":
    print("🔑 Décodeur de token JWT")
    print("=" * 80)
    
    # Demander le token
    print("\nCollez votre token JWT (ou appuyez sur Entrée pour utiliser celui du .env):")
    token = input().strip()
    
    if not token:
        # Charger depuis .env
        from dotenv import load_dotenv
        import os
        load_dotenv()
        token = os.getenv('SPIDER_VISION_JWT_TOKEN')
        if token:
            print(f"\n✅ Token chargé depuis .env")
        else:
            print("\n❌ Aucun token trouvé dans .env")
            exit(1)
    
    decode_jwt(token)
