#!/usr/bin/env python3
"""Script de test pour générer un rapport complet avec Spider Vision."""

import os
import sys
from pathlib import Path
from datetime import date, timedelta

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from cli.ioc import get_container
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_full_report_generation():
    """Tester la génération complète d'un rapport."""
    load_dotenv()
    
    print("🚀 Test de génération complète du rapport dealer")
    print("-" * 50)
    
    try:
        # Initialiser le container
        container = get_container()
        report_service = container.report_service()
        
        # Générer le rapport pour aujourd'hui
        today = date.today()
        print(f"📅 Génération du rapport pour: {today}")
        
        # Test avec format HTML
        print("\n📄 Génération du rapport HTML...")
        html_path = report_service.generate_dealer_report(
            date_from=today,
            date_to=today,
            dealer=None,  # Tous les dealers
            fmt='html'
        )
        
        print(f"✅ Rapport HTML généré: {html_path}")
        
        # Vérifier que le fichier existe
        if Path(html_path).exists():
            file_size = Path(html_path).stat().st_size
            print(f"📊 Taille du fichier: {file_size} bytes")
            
            # Lire un extrait du contenu
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Rapport Dealer" in content:
                    print("✅ Contenu HTML valide détecté")
                else:
                    print("⚠️ Contenu HTML suspect")
        else:
            print("❌ Fichier HTML non trouvé")
            return False
        
        # Test avec format CSV
        print("\n📊 Génération du rapport CSV...")
        csv_path = report_service.generate_dealer_report(
            date_from=today,
            date_to=today,
            dealer=None,
            fmt='csv'
        )
        
        print(f"✅ Rapport CSV généré: {csv_path}")
        
        # Vérifier le CSV
        if Path(csv_path).exists():
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"📊 Nombre de lignes CSV: {len(lines)}")
                if len(lines) > 0:
                    print(f"📋 En-tête: {lines[0].strip()}")
        
        # Test avec un dealer spécifique
        print("\n🏪 Test avec un dealer spécifique (Carrefour)...")
        specific_path = report_service.generate_dealer_report(
            date_from=today,
            date_to=today,
            dealer='Carrefour',
            fmt='html'
        )
        print(f"✅ Rapport spécifique généré: {specific_path}")
        
        print("\n🎉 Tous les tests de génération sont passés!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        logger.exception("Erreur détaillée:")
        return False

def test_services():
    """Tester les autres services (GCS, Teams)."""
    print("\n🔧 Test des services additionnels")
    print("-" * 30)
    
    try:
        container = get_container()
        
        # Test GCS Publisher (sans upload réel)
        print("☁️ Test GCS Publisher...")
        gcs_publisher = container.gcs_publisher()
        print("✅ GCS Publisher initialisé")
        
        # Test Teams Notifier (sans envoi réel)
        print("📢 Test Teams Notifier...")
        teams_notifier = container.teams_notifier()
        print("✅ Teams Notifier initialisé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des services: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS COMPLETS DU PROJET DEALER-REPORT")
    print("=" * 60)
    
    success1 = test_full_report_generation()
    success2 = test_services()
    
    overall_success = success1 and success2
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("\n📋 Prochaines étapes:")
        print("1. Configurer vos credentials GCP pour l'upload")
        print("2. Configurer votre webhook Teams")
        print("3. Tester le pipeline complet avec: dealer-report generate_dealer_report")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les logs ci-dessus pour plus de détails")
    
    sys.exit(0 if overall_success else 1)
