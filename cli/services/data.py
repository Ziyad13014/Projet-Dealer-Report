"""Module de récupération des données depuis l'API SpiderVision."""

import logging
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class SpiderVisionData:
    """Gestionnaire de récupération des données depuis l'API SpiderVision."""
    
    def __init__(self):
        self.api_base = os.getenv('SPIDER_VISION_API_BASE', 'https://food-api-spider-vision.data-solutions.com')
        self.overview_endpoint = os.getenv('SPIDER_VISION_OVERVIEW_ENDPOINT', '/store-history/overview')
        
    def get_overview(self, token: str) -> Dict[str, Any]:
        """
        Récupère les données overview depuis l'API SpiderVision.
        
        Args:
            token: Token JWT d'authentification
            
        Returns:
            Dict[str, Any]: Données JSON de l'overview
            
        Raises:
            RuntimeError: En cas d'échec de récupération
        """
        if not token:
            raise RuntimeError("Token d'authentification requis")
        
        overview_url = f"{self.api_base.rstrip('/')}{self.overview_endpoint}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            logger.info(f"Récupération des données overview depuis {overview_url}")
            response = requests.get(overview_url, headers=headers, timeout=30)
            
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Données récupérées avec succès ({len(str(data))} caractères)")
                return data
            else:
                error_msg = f"Échec de récupération des données: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    error_msg += f" - {response.text}"
                
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Erreur de connexion lors de la récupération: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_retailers_data(self, token: str) -> Dict[str, Any]:
        """
        Récupère les données des retailers (alias pour get_overview).
        
        Args:
            token: Token JWT d'authentification
            
        Returns:
            Dict[str, Any]: Données JSON des retailers
        """
        return self.get_overview(token)
    
    def get_store_history(self, token: str, store_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère l'historique des magasins.
        
        Args:
            token: Token JWT d'authentification
            store_id: ID du magasin spécifique (optionnel)
            
        Returns:
            Dict[str, Any]: Données JSON de l'historique
        """
        endpoint = self.overview_endpoint
        if store_id:
            endpoint = f"/store-history/{store_id}"
        
        url = f"{self.api_base.rstrip('/')}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            logger.info(f"Récupération de l'historique depuis {url}")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Échec de récupération de l'historique: {response.status_code}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Erreur de connexion: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

# Fonction utilitaire pour une utilisation simple
def get_overview(token: str) -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer les données overview.
    
    Args:
        token: Token JWT d'authentification
        
    Returns:
        Dict[str, Any]: Données JSON de l'overview
    """
    data_service = SpiderVisionData()
    return data_service.get_overview(token)
