"""
Script pour mettre à jour automatiquement le lien du dernier rapport dans index.html
"""
import os
import re
from pathlib import Path


def get_latest_report(reports_dir='reports'):
    """
    Récupère le nom du dernier fichier de rapport généré.
    
    Args:
        reports_dir: Chemin vers le dossier des rapports
        
    Returns:
        str: Nom du fichier du dernier rapport (ex: 'last_day_history_live_report_20250930_103145.html')
    """
    reports_path = Path(reports_dir)
    
    # Chercher tous les fichiers HTML de rapport
    report_files = list(reports_path.glob('last_day_history_live_report_*.html'))
    
    if not report_files:
        print("⚠️ Aucun rapport trouvé dans le dossier reports/")
        return None
    
    # Trier par date de modification (le plus récent en premier)
    latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
    
    return latest_report.name


def update_index_html(latest_report_filename, index_path='index.html'):
    """
    Met à jour le lien du dernier rapport dans index.html.
    
    Args:
        latest_report_filename: Nom du fichier du dernier rapport
        index_path: Chemin vers le fichier index.html
        
    Returns:
        bool: True si la mise à jour a réussi, False sinon
    """
    if not latest_report_filename:
        print("❌ Aucun fichier de rapport fourni")
        return False
    
    index_file = Path(index_path)
    
    if not index_file.exists():
        print(f"❌ Le fichier {index_path} n'existe pas")
        return False
    
    # Lire le contenu du fichier index.html
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {index_path}: {e}")
        return False
    
    # Nouveau lien vers le rapport
    new_href = f"reports/{latest_report_filename}"
    
    # Pattern pour trouver le lien du dernier rapport
    # Cherche : <a href="reports/..." class="btn">
    pattern = r'(<a\s+href=")[^"]*("\s+class="btn">[\s\S]*?📈\s*Voir le Dernier Rapport)'
    
    # Vérifier si le pattern existe
    if re.search(pattern, content):
        # Remplacer le href existant
        updated_content = re.sub(pattern, rf'\g<1>{new_href}\g<2>', content)
        action = "mis à jour"
    else:
        print("⚠️ Pattern du bouton 'Dernier Rapport' non trouvé dans index.html")
        return False
    
    # Sauvegarder le fichier mis à jour
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ index.html {action} avec succès")
        print(f"   Nouveau lien: {new_href}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture de {index_path}: {e}")
        return False


def update_last_report_symlink(latest_report_filename, reports_dir='reports'):
    """
    Crée ou met à jour le fichier last_day_history_live_report.html
    pour qu'il soit une copie du dernier rapport.
    
    Args:
        latest_report_filename: Nom du fichier du dernier rapport
        reports_dir: Chemin vers le dossier des rapports
    """
    if not latest_report_filename:
        return False
    
    reports_path = Path(reports_dir)
    source_file = reports_path / latest_report_filename
    target_file = reports_path / 'last_day_history_live_report.html'
    
    try:
        # Copier le contenu du dernier rapport vers le fichier "latest"
        with open(source_file, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(target_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"✅ Fichier last_day_history_live_report.html mis à jour")
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de la mise à jour du symlink: {e}")
        return False


def auto_update_index():
    """
    Fonction principale pour automatiser la mise à jour de index.html
    """
    print("🔄 Mise à jour automatique de index.html...")
    
    # 1. Récupérer le dernier rapport
    latest_report = get_latest_report()
    
    if not latest_report:
        print("❌ Impossible de trouver le dernier rapport")
        return False
    
    print(f"📊 Dernier rapport trouvé: {latest_report}")
    
    # 2. Mettre à jour index.html
    success = update_index_html(latest_report)
    
    # 3. Mettre à jour le fichier "latest" pour GitHub Pages
    update_last_report_symlink(latest_report)
    
    return success


if __name__ == "__main__":
    auto_update_index()
