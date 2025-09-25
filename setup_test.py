#!/usr/bin/env python3
"""Script de diagnostic pour identifier les problèmes du projet dealer-report."""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Vérifier la version Python."""
    print("🐍 Vérification de Python...")
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("❌ Python 3.12+ requis")
        return False
    else:
        print("✅ Version Python OK")
        return True

def check_dependencies():
    """Vérifier les dépendances."""
    print("\n📦 Vérification des dépendances...")
    
    # Mapping des noms de packages pip vers les noms d'import
    package_mapping = {
        'click': 'click',
        'python-dotenv': 'dotenv',
        'dependency-injector': 'dependency_injector',
        'PyMySQL': 'pymysql',
        'google-cloud-storage': 'google.cloud.storage',
        'requests': 'requests'
    }
    
    missing = []
    for pip_name, import_name in package_mapping.items():
        try:
            if '.' in import_name:
                # Pour les packages avec sous-modules comme google.cloud.storage
                parts = import_name.split('.')
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(import_name)
            print(f"✅ {pip_name}")
        except (ImportError, AttributeError):
            print(f"❌ {pip_name} manquant")
            missing.append(pip_name)
    
    return len(missing) == 0, missing

def check_env_file():
    """Vérifier le fichier .env."""
    print("\n🔧 Vérification du fichier .env...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Fichier .env manquant")
        return False
    
    required_vars = [
        'SPIDER_VISION_URL', 'SPIDER_VISION_USERNAME', 'SPIDER_VISION_PASSWORD'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} manquant")
        else:
            print(f"✅ {var} configuré")
    
    return len(missing_vars) == 0

def check_project_structure():
    """Vérifier la structure du projet."""
    print("\n📁 Vérification de la structure du projet...")
    
    required_files = [
        'cli/__init__.py',
        'cli/cli.py',
        'cli/ioc.py',
        'cli/repository/WebDataRepository.py',
        'cli/services/ReportService.py',
        'cli/services/GcsPublisher.py',
        'cli/services/TeamsNotifier.py',
        'pyproject.toml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ {file_path} manquant")
        else:
            print(f"✅ {file_path}")
    
    return len(missing_files) == 0

def test_imports():
    """Tester les imports du projet."""
    print("\n🔍 Test des imports...")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        
        from cli.ioc import get_container
        print("✅ Import cli.ioc OK")
        
        from cli.repository.WebDataRepository import WebDataRepository
        print("✅ Import WebDataRepository OK")
        
        from cli.services.ReportService import ReportService
        print("✅ Import ReportService OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_container():
    """Tester l'initialisation du container."""
    print("\n🏗️ Test du container DI...")
    
    try:
        from cli.ioc import get_container
        container = get_container()
        
        # Test des services
        repo = container.web_data_repository()
        print("✅ WebDataRepository initialisé")
        
        report_service = container.report_service()
        print("✅ ReportService initialisé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur container: {e}")
        return False

def install_missing_dependencies(missing_packages):
    """Installer les dépendances manquantes."""
    if not missing_packages:
        return True
    
    print(f"\n📥 Installation des dépendances manquantes: {', '.join(missing_packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", "."
        ])
        print("✅ Installation réussie")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur d'installation: {e}")
        return False

def main():
    """Fonction principale de diagnostic."""
    print("🔍 DIAGNOSTIC DU PROJET DEALER-REPORT")
    print("=" * 50)
    
    # Changer vers le répertoire du projet
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    all_ok = True
    
    # 1. Vérifier Python
    if not check_python_version():
        all_ok = False
    
    # 2. Vérifier la structure
    if not check_project_structure():
        all_ok = False
    
    # 3. Vérifier .env
    if not check_env_file():
        all_ok = False
    
    # 4. Vérifier les dépendances
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        all_ok = False
        # Essayer d'installer
        if install_missing_dependencies(missing):
            deps_ok, missing = check_dependencies()
            if deps_ok:
                print("✅ Dépendances installées avec succès")
    
    # 5. Tester les imports
    if deps_ok and not test_imports():
        all_ok = False
    
    # 6. Tester le container
    if deps_ok and not test_container():
        all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 DIAGNOSTIC RÉUSSI - Le projet est prêt!")
        print("\n📋 Prochaines étapes:")
        print("1. Exécuter: python test_connection.py")
        print("2. Exécuter: python test_full_report.py")
        print("3. Tester: dealer-report generate_dealer_report")
    else:
        print("❌ PROBLÈMES DÉTECTÉS - Corrigez les erreurs ci-dessus")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
