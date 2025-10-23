#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer un nouveau token JWT valide depuis l'API SpiderVision
"""

import sys
import os
from pathlib import Path

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ajouter le dossier parent au path pour importer depuis src
sys.path.insert(0, str(Path(__file__).parent.parent))

def update_env_token(new_token):
    """Met à jour le token JWT dans le fichier .env"""
    env_path = Path(__file__).parent.parent / '.env'
    
    try:
        # Lire le fichier .env actuel
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Chercher et remplacer la ligne SPIDER_VISION_JWT_TOKEN
        token_found = False
        for i, line in enumerate(lines):
            if line.startswith('SPIDER_VISION_JWT_TOKEN='):
                lines[i] = f'SPIDER_VISION_JWT_TOKEN={new_token}\n'
                token_found = True
                break
        
        # Si la ligne n'existe pas, l'ajouter à la fin
        if not token_found:
            # Ajouter une ligne vide si le fichier ne se termine pas par \n
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append(f'SPIDER_VISION_JWT_TOKEN={new_token}\n')
        
        # Réécrire le fichier .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de la mise à jour du .env: {e}")
        return False

def generate_new_jwt_token():
    """Génère un nouveau token JWT en se connectant à l'API SpiderVision"""
    print("🔑 Génération d'un nouveau token JWT...")
    print("=" * 80)
    
    try:
        # Importer depuis le module src
        from src.cli.services.auth import SpiderVisionAuth
        from dotenv import load_dotenv
        import os
        
        # Charger et afficher les variables (masquées)
        load_dotenv()
        email = os.getenv('SPIDER_VISION_EMAIL')
        password = os.getenv('SPIDER_VISION_PASSWORD')
        api_base = os.getenv('SPIDER_VISION_API_BASE')
        
        print(f"📧 Email utilisé: {email[:3]}***{email[-10:] if email else 'NON DÉFINI'}")
        print(f"🔐 Password: {'*' * (len(password) if password else 0)} ({len(password) if password else 0} caractères)")
        print(f"🌐 API Base: {api_base}")
        print("=" * 80)
        
        print("🔄 Connexion à l'API SpiderVision...")
        
        auth = SpiderVisionAuth()
        token = auth.login()
        
        print("✅ Authentification réussie !")
        print("=" * 80)
        print("\n🎉 NOUVEAU TOKEN JWT GÉNÉRÉ :\n")
        print("=" * 80)
        print(token[:50] + "..." + token[-20:])  # Afficher partiellement pour sécurité
        print("=" * 80)
        
        # Mise à jour automatique du fichier .env
        print("\n🔄 Mise à jour automatique du fichier .env...")
        if update_env_token(token):
            print("✅ Fichier .env mis à jour avec succès !")
            print("\n📋 PROCHAINES ÉTAPES :")
            print("1. Le token a été automatiquement enregistré dans .env")
            print("2. Vous pouvez maintenant générer un rapport :")
            print("   → python src\\generate_new_report.py")
            print("\n✅ Le nouveau token sera valide pendant environ 2 heures.")
        else:
            print("❌ Échec de la mise à jour automatique du .env")
            print("\n📋 MISE À JOUR MANUELLE REQUISE :")
            print("1. Ouvrez le fichier .env")
            print("2. Remplacez la valeur de SPIDER_VISION_JWT_TOKEN par :")
            print(f"   {token}")
            print("3. Sauvegardez le fichier .env")
        
        print("=" * 80)
        
        return token
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la génération du token :")
        print(f"   {str(e)}")
        print("\n💡 Vérifiez que :")
        print("   - Le fichier .env contient SPIDER_VISION_EMAIL et SPIDER_VISION_PASSWORD")
        print("   - Les identifiants sont corrects")
        print("   - Vous avez une connexion internet")
        print("\n🔍 DEBUG - Valeurs actuelles dans .env :")
        print(f"   Email: {email if email else '❌ NON DÉFINI'}")
        print(f"   Password: {'✅ Défini' if password else '❌ NON DÉFINI'}")
        print(f"   API Base: {api_base if api_base else '❌ NON DÉFINI'}")
        return None

def create_automation_files():
    """Crée tous les fichiers nécessaires pour l'automatisation"""
    
    # 1. Créer requirements.txt
    requirements_content = """click
python-dotenv
dependency-injector
PyMySQL
google-cloud-storage
requests
beautifulsoup4
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content.strip() + "\n")
    print("✅ requirements.txt créé")
    
    # 2. Créer le dossier .github/workflows
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Dossier .github/workflows créé")
    
    # 3. Créer le workflow GitHub Actions
    workflow_content = """name: 📊 Daily SpiderVision Report

on:
  # Exécution quotidienne à 07:30 UTC (09:30 heure de Paris en été)
  schedule:
    - cron: "30 7 * * *"
  
  # Permet l'exécution manuelle depuis GitHub
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🐍 Setup Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'pip'

      - name: 📦 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 📊 Generate SpiderVision Report
        env:
          SPIDER_VISION_API_BASE: ${{ secrets.SPIDER_VISION_API_BASE }}
          SPIDER_VISION_EMAIL: ${{ secrets.SPIDER_VISION_EMAIL }}
          SPIDER_VISION_PASSWORD: ${{ secrets.SPIDER_VISION_PASSWORD }}
          SPIDER_VISION_JWT_TOKEN: ${{ secrets.SPIDER_VISION_JWT_TOKEN }}
          SPIDER_VISION_LOGIN_ENDPOINT: ${{ secrets.SPIDER_VISION_LOGIN_ENDPOINT }}
          SPIDER_VISION_OVERVIEW_ENDPOINT: ${{ secrets.SPIDER_VISION_OVERVIEW_ENDPOINT }}
        run: |
          echo "🔄 Génération du rapport en cours..."
          python generate_new_report.py
          echo "✅ Rapport généré avec succès !"

      - name: 📤 Upload report as artifact
        uses: actions/upload-artifact@v4
        with:
          name: spidervision-report-${{ github.run_number }}
          path: |
            reports/last_day_history_live_report_*.html
            reports/spider_vision_overview_current.csv
            index.html
          retention-days: 30

      - name: 📝 Create summary
        run: |
          echo "## 📊 Rapport SpiderVision généré" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "✅ Le rapport a été généré avec succès !" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "📅 Date: $(date)" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "📥 Téléchargez le rapport depuis l'onglet 'Artifacts' ci-dessus." >> $GITHUB_STEP_SUMMARY
          
          # Lister les fichiers générés
          if [ -d "reports" ]; then
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "### Fichiers générés:" >> $GITHUB_STEP_SUMMARY
            ls -lh reports/*.html | tail -5 | awk '{print "- " $9 " (" $5 ")"}' >> $GITHUB_STEP_SUMMARY
          fi
"""
    
    workflow_file = workflows_dir / "daily-report.yml"
    with open(workflow_file, "w", encoding="utf-8") as f:
        f.write(workflow_content)
    print(f"✅ {workflow_file} créé")
    
    # 4. Créer un fichier d'instructions
    instructions = """# 🚀 Automatisation GitHub Actions - Instructions

## ✅ Fichiers créés avec succès !

Les fichiers suivants ont été créés :
- ✅ requirements.txt
- ✅ .github/workflows/daily-report.yml

## 📋 Prochaines étapes :

### 1. Vérifier les fichiers créés
Ouvrez les fichiers pour vérifier qu'ils sont corrects.

### 2. Ajouter et commiter sur Git
```bash
git add requirements.txt .github/workflows/daily-report.yml
git commit -m "🤖 Ajout automatisation quotidienne via GitHub Actions"
git push
```

### 3. Configurer les secrets GitHub
Allez sur GitHub → Votre dépôt → Settings → Secrets and variables → Actions

Ajoutez ces secrets (copiez les valeurs depuis votre fichier .env) :

| Nom du secret | Valeur |
|---------------|--------|
| SPIDER_VISION_API_BASE | https://food-api-spider-vision.data-solutions.com |
| SPIDER_VISION_EMAIL | Votre email |
| SPIDER_VISION_PASSWORD | Votre mot de passe |
| SPIDER_VISION_JWT_TOKEN | Votre token JWT (si vous en avez un) |
| SPIDER_VISION_LOGIN_ENDPOINT | /admin-user/sign-in |
| SPIDER_VISION_OVERVIEW_ENDPOINT | /store-history/overview |

### 4. Tester le workflow
1. Allez sur GitHub → Actions
2. Cliquez sur "📊 Daily SpiderVision Report"
3. Cliquez sur "Run workflow" → "Run workflow"
4. Attendez que le workflow se termine
5. Téléchargez le rapport depuis "Artifacts"

## 🎉 C'est tout !

Votre rapport sera généré automatiquement tous les jours à 09:30 (heure de Paris).
"""
    
    with open("GITHUB_ACTIONS_SETUP.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    print("✅ GITHUB_ACTIONS_SETUP.md créé")
    
    print("\n" + "="*60)
    print("🎉 TOUS LES FICHIERS ONT ÉTÉ CRÉÉS AVEC SUCCÈS !")
    print("="*60)
    print("\nConsultez le fichier GITHUB_ACTIONS_SETUP.md pour les instructions.")

if __name__ == "__main__":
    # Par défaut, générer un nouveau token JWT
    generate_new_jwt_token()
