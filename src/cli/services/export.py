"""Module d'export des données en CSV et Excel."""

import csv
import logging
import os
from typing import Dict, Any, List, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class DataExporter:
    """Gestionnaire d'export des données en différents formats."""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_to_csv(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str = "overview.csv") -> str:
        """
        Sauvegarde les données en format CSV.
        
        Args:
            data: Données à exporter (dict ou liste de dicts)
            filename: Nom du fichier de sortie
            
        Returns:
            str: Chemin complet du fichier créé
            
        Raises:
            RuntimeError: En cas d'erreur d'export
        """
        try:
            # Normaliser les données en liste
            if isinstance(data, dict):
                # Si c'est un dict, vérifier s'il contient une liste de données
                if 'data' in data and isinstance(data['data'], list):
                    rows = data['data']
                elif 'items' in data and isinstance(data['items'], list):
                    rows = data['items']
                elif 'retailers' in data and isinstance(data['retailers'], list):
                    rows = data['retailers']
                else:
                    # Sinon traiter le dict comme une seule ligne
                    rows = [data]
            elif isinstance(data, list):
                rows = data
            else:
                raise RuntimeError(f"Format de données non supporté: {type(data)}")
            
            if not rows:
                raise RuntimeError("Aucune donnée à exporter")
            
            # Créer le chemin complet
            filepath = self.output_dir / filename
            
            # Extraire toutes les clés possibles de tous les objets
            all_keys = set()
            for row in rows:
                if isinstance(row, dict):
                    all_keys.update(row.keys())
            
            if not all_keys:
                raise RuntimeError("Aucune clé trouvée dans les données")
            
            fieldnames = sorted(list(all_keys))
            
            # Écrire le CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in rows:
                    if isinstance(row, dict):
                        # Remplir les valeurs manquantes avec None
                        normalized_row = {key: row.get(key, None) for key in fieldnames}
                        writer.writerow(normalized_row)
            
            logger.info(f"Données exportées vers {filepath} ({len(rows)} lignes)")
            return str(filepath)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export CSV: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def save_to_excel(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str = "overview.xlsx") -> str:
        """
        Sauvegarde les données en format Excel.
        
        Args:
            data: Données à exporter (dict ou liste de dicts)
            filename: Nom du fichier de sortie
            
        Returns:
            str: Chemin complet du fichier créé
        """
        try:
            import pandas as pd
            
            # Normaliser les données
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    df_data = data['data']
                elif 'items' in data and isinstance(data['items'], list):
                    df_data = data['items']
                elif 'retailers' in data and isinstance(data['retailers'], list):
                    df_data = data['retailers']
                else:
                    df_data = [data]
            elif isinstance(data, list):
                df_data = data
            else:
                raise RuntimeError(f"Format de données non supporté: {type(data)}")
            
            # Créer le DataFrame
            df = pd.DataFrame(df_data)
            
            # Créer le chemin complet
            filepath = self.output_dir / filename
            
            # Sauvegarder en Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Données exportées vers {filepath} ({len(df)} lignes)")
            return str(filepath)
            
        except ImportError:
            logger.warning("pandas et openpyxl requis pour l'export Excel. Utilisation du CSV à la place.")
            csv_filename = filename.replace('.xlsx', '.csv').replace('.xls', '.csv')
            return self.save_to_csv(data, csv_filename)
        except Exception as e:
            error_msg = f"Erreur lors de l'export Excel: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def save_overview_data(self, data: Dict[str, Any], format: str = "csv") -> str:
        """
        Sauvegarder les données overview dans le format spécifié.
        
        Args:
            data: Données JSON à sauvegarder
            format: Format de sortie ('csv', 'excel' ou 'html')
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "excel":
            filename = f"spider_vision_overview_{timestamp}.xlsx"
            return self.save_to_excel(data, filename)
        elif format.lower() == "html":
            filename = f"spider_vision_overview_{timestamp}.html"
            return self.save_to_html(data, filename)
        else:
            filename = f"spider_vision_overview_{timestamp}.csv"
            return self.save_to_csv(data, filename)
    
    def save_to_html(self, data: Dict[str, Any], filename: str) -> str:
        """
        Sauvegarder les données en format HTML.
        
        Args:
            data: Données JSON à sauvegarder
            filename: Nom du fichier de sortie
            
        Returns:
            str: Chemin complet du fichier sauvegardé
        """
        try:
            from cli.services.html_export import HTMLExporter
            
            # Créer le répertoire reports s'il n'existe pas
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Chemin complet du fichier
            filepath = os.path.join(reports_dir, filename)
            
            # Générer le rapport HTML
            html_exporter = HTMLExporter()
            output_path = html_exporter.generate_html_report(data, filepath)
            
            logger.info(f"Données sauvegardées en HTML: {output_path}")
            return os.path.abspath(output_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde HTML: {e}")
            raise

# Fonctions utilitaires pour une utilisation simple
def save_to_csv(data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str = "overview.csv") -> str:
    """
    Fonction utilitaire pour sauvegarder en CSV.
    
    Args:
        data: Données à exporter
        filename: Nom du fichier
        
    Returns:
        str: Chemin du fichier créé
    """
    exporter = DataExporter()
    return exporter.save_to_csv(data, filename)

def save_to_excel(data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str = "overview.xlsx") -> str:
    """
    Fonction utilitaire pour sauvegarder en Excel.
    
    Args:
        data: Données à exporter
        filename: Nom du fichier
        
    Returns:
        str: Chemin du fichier créé
    """
    exporter = DataExporter()
    return exporter.save_to_excel(data, filename)
