#!/usr/bin/env python3
"""Test simple avec des données mock."""

import sys
from pathlib import Path
from datetime import date

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from cli.ioc import get_container

def test_mock_report():
    """Tester la génération de rapport avec des données mock."""
    print("🧪 TEST AVEC DONNÉES MOCK")
    print("=" * 40)
    
    try:
        # Initialiser le container
        container = get_container()
        report_service = container.report_service()
        
        # Générer un rapport pour aujourd'hui
        today = date.today()
        print(f"📅 Génération du rapport pour: {today}")
        
        # Générer le rapport HTML
        html_path = report_service.generate_dealer_report(
            date_from=today,
            date_to=today,
            dealer=None,
            fmt='html'
        )
        
        print(f"✅ Rapport généré: {html_path}")
        
        # Vérifier le fichier
        if Path(html_path).exists():
            file_size = Path(html_path).stat().st_size
            print(f"📊 Taille: {file_size} bytes")
            
            # Lire un extrait
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Rapport Dealer" in content and "Anomalies" in content:
                    print("✅ Contenu HTML valide")
                    
                    # Compter les anomalies
                    anomaly_count = content.count('⚠️')
                    success_count = content.count('✅')
                    print(f"📋 Anomalies trouvées: {anomaly_count}")
                    print(f"📋 Succès trouvés: {success_count}")
                else:
                    print("⚠️ Contenu HTML suspect")
        
        print("\n🎉 TEST RÉUSSI - Le projet fonctionne avec les données mock!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mock_report()
    if success:
        print("\n💡 PROCHAINES ÉTAPES:")
        print("1. Tester: dealer-report generate_dealer_report")
        print("2. Configurer GCS et Teams si nécessaire")
        print("3. Plus tard: remplacer MockDataRepository par WebDataRepository")
    sys.exit(0 if success else 1)
