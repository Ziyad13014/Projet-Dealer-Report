#!/usr/bin/env python3
"""
Script de création des fichiers d'automatisation GitHub Actions
"""

import os
from pathlib import Path

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
    create_automation_files()
