"""Module d'authentification pour l'API SpiderVision."""

import logging
import os
import requests
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class SpiderVisionAuth:
    """Gestionnaire d'authentification pour l'API SpiderVision."""
    
    def __init__(self):
        """Initialiser le service d'authentification SpiderVision"""
        load_dotenv()
        
        self.api_base = os.getenv("SPIDER_VISION_API_BASE")
        self.email = os.getenv("SPIDER_VISION_EMAIL")
        self.password = os.getenv("SPIDER_VISION_PASSWORD")
        self.login_endpoint = os.getenv("SPIDER_VISION_LOGIN_ENDPOINT", "/admin-user/sign-in")
        
        # Vérifier s'il y a un token JWT pré-configuré
        self._token = os.getenv("SPIDER_VISION_JWT_TOKEN")
        
        if not self.api_base:
            raise ValueError("SPIDER_VISION_API_BASE manquant dans .env")
        
        # Si pas de token pré-configuré, vérifier les credentials pour login
        if not self._token and not all([self.email, self.password]):
            raise ValueError("Token JWT ou credentials (email/password) manquants dans .env")
    
    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> str:
        """
        Authentification via l'API SpiderVision.
        
        Args:
            email: Email de connexion (optionnel, utilise .env par défaut)
            password: Mot de passe (optionnel, utilise .env par défaut)
            
        Returns:
            str: Token JWT
        
        Raises:
            RuntimeError: En cas d'échec d'authentification
        """
        # Si un token JWT est déjà configuré dans .env, l'utiliser directement
        if self._token and not email and not password:
            logger.info("Utilisation du token JWT pré-configuré")
            return self._token
        
        # Utiliser les paramètres fournis ou ceux de l'environnement
        auth_email = email or self.email
        auth_password = password or self.password
        
        if not auth_email or not auth_password:
            raise ValueError("Email et mot de passe requis pour l'authentification")
        
        login_url = f"{self.api_base.rstrip('/')}{self.login_endpoint}"
        
        payload = {
            "email": auth_email,
            "password": auth_password
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            logger.info(f"Tentative d'authentification sur {login_url}")
            response = requests.post(login_url, json=payload, headers=headers, timeout=30)
            
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                data = response.json()
                logger.debug(f"Response data keys: {list(data.keys())}")
                
                # Chercher le token dans différents champs possibles
                token = (data.get("token") or 
                        data.get("access_token") or 
                        data.get("jwt") or
                        data.get("accessToken") or
                        data.get("authToken"))
                
                if not token:
                    logger.error(f"Token non trouvé dans la réponse. Champs disponibles: {list(data.keys())}")
                    raise RuntimeError("Impossible de trouver le token dans la réponse login")
                
                self._token = token
                logger.info("Authentification réussie")
                return token
                
            else:
                error_msg = f"Échec d'authentification: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    error_msg += f" - {response.text}"
                
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Erreur de connexion lors de l'authentification: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_token(self) -> Optional[str]:
        """Retourne le token actuel (peut être None si pas encore authentifié)."""
        return self._token
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié."""
        return self._token is not None
    
    def logout(self):
        """Déconnexion (supprime le token local)."""
        self._token = None
        logger.info("Déconnexion effectuée")

# Fonction utilitaire pour une utilisation simple
def login(email: Optional[str] = None, password: Optional[str] = None) -> str:
    """
    Fonction utilitaire pour l'authentification rapide.
    
    Args:
        email: Email de connexion (optionnel, utilise .env par défaut)
        password: Mot de passe (optionnel, utilise .env par défaut)
        
    Returns:
        str: Token JWT
    """
    auth = SpiderVisionAuth()
    return auth.login(email, password)
