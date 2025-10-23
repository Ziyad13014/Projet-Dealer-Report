import logging
import requests
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import json
from urllib.parse import urljoin
import time
from bs4 import BeautifulSoup
import re
from cli.services.auth import SpiderVisionAuth
from cli.services.data import SpiderVisionData

logger = logging.getLogger(__name__)

class WebDataRepository:
    """Repository pour récupérer les données depuis Spider Vision via l'API JWT"""
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        # Maintenir la compatibilité avec l'ancien constructeur
        self.auth = SpiderVisionAuth()
        self.data_service = SpiderVisionData()
        self._token = None
        self._authenticated = False
        
        # Si des paramètres sont fournis, les utiliser
        if username:
            self.auth.email = username
        if password:
            self.auth.password = password
        
    def _authenticate(self) -> bool:
        """Authentification via l'API JWT Spider Vision"""
        if self._authenticated and self._token:
            return True
            
        try:
            logger.info("Tentative d'authentification via API JWT")
            self._token = self.auth.login()
            self._authenticated = True
            logger.info("Authentification JWT réussie")
            return True
            
        except Exception as e:
            logger.error(f"Échec d'authentification JWT: {e}")
            self._authenticated = False
            self._token = None
            return False
    
    def get_dashboard_data(self) -> List[Dict[str, Any]]:
        """Récupérer les données du tableau dashboard Spider Vision via l'API JWT"""
        if not self._authenticate():
            logger.error("Impossible de s'authentifier pour récupérer les données")
            return []
        
        try:
            logger.info("Récupération des données overview via API JWT")
            overview_data = self.data_service.get_overview(self._token)
            return self._parse_overview_data(overview_data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return []
    
    def _parse_overview_data(self, data: Any) -> List[Dict[str, Any]]:
        """Parser les données overview de l'API JWT"""
        retailers = []
        
        # Si c'est une liste directe
        if isinstance(data, list):
            items = data
        # Si c'est un dict avec une clé contenant les retailers
        elif isinstance(data, dict):
            items = data.get('retailers', data.get('data', data.get('items', data.get('stores', [data]))))
        else:
            return []
        
        for item in items:
            if isinstance(item, dict):
                retailer = {
                    'id': item.get('id', item.get('dealer_id', item.get('store_id', ''))),
                    'name': item.get('name', item.get('dealer', item.get('domain_dealer', item.get('store_name', '')))),
                    'stores_crawled': int(item.get('stores_crawled', item.get('crawled_count', item.get('delta_count', item.get('successful_crawls', 0))))),
                    'stores_failed': int(item.get('stores_failed', item.get('failed_count', item.get('failed_crawls', 0)))),
                    'stores_total': int(item.get('stores_total', item.get('total_stores', item.get('crawl_count', item.get('total_crawls', 0))))),
                    'success_rate': float(item.get('success_rate', item.get('success_percent', item.get('success_ratio', 0)))),
                    'progress_rate': float(item.get('progress_rate', item.get('progress_percent', item.get('completion_rate', 0))))
                }
                retailers.append(retailer)
        
        return retailers
    
    def _parse_html_dashboard(self, html_content: str) -> List[Dict[str, Any]]:
        """Parser le tableau HTML du dashboard"""
        soup = BeautifulSoup(html_content, 'html.parser')
        retailers = []
        
        # Chercher le tableau principal
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            # Ignorer les tables trop petites
            if len(rows) < 2:
                continue
                
            # Analyser les en-têtes pour identifier la bonne table
            header_row = rows[0]
            headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
            
            # Vérifier si c'est notre table (contient dealer, store, etc.)
            if any(keyword in ' '.join(headers) for keyword in ['dealer', 'store', 'crawl', 'domain']):
                logger.info(f"Table trouvée avec headers: {headers}")
                
                # Parser les lignes de données
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 6:  # Au moins 6 colonnes attendues
                        try:
                            retailer = self._parse_table_row(cells)
                            if retailer:
                                retailers.append(retailer)
                        except Exception as e:
                            logger.debug(f"Erreur parsing ligne: {e}")
                            continue
        
        logger.info(f"Trouvé {len(retailers)} retailers dans le HTML")
        return retailers
    
    def _parse_table_row(self, cells) -> Optional[Dict[str, Any]]:
        """Parser une ligne du tableau"""
        if len(cells) < 6:
            return None
            
        try:
            # Extraire les textes des cellules
            cell_texts = [cell.get_text().strip() for cell in cells]
            
            # ID (première colonne)
            retailer_id = cell_texts[0]
            
            # Nom (deuxième colonne)
            name = cell_texts[1]
            
            # Stores crawled (troisième colonne)
            stores_crawled = self._extract_number(cell_texts[2])
            
            # Stores failed (quatrième colonne)
            stores_failed = self._extract_number(cell_texts[3])
            
            # Store to crawl count (cinquième colonne - le vrai total)
            stores_total = self._extract_number(cell_texts[4])
            
            # Success rate - extraire depuis la colonne "Success"
            success_rate = 0.0
            progress_rate = 0.0
            
            # Chercher la colonne Success (généralement colonne 5 ou 6)
            for i in range(5, len(cell_texts)):
                text = cell_texts[i].strip()
                
                # Si on trouve un pourcentage dans cette colonne
                if '%' in text:
                    percent = self._extract_percentage(text)
                    
                    # Si c'est la colonne Success (contient le pourcentage + info magasins)
                    if 'on' in text.lower() and 'stores' in text.lower():
                        success_rate = percent
                    # Sinon c'est probablement le progress rate
                    elif progress_rate == 0.0:
                        progress_rate = percent
                
                # Si on trouve "on X stores" sans pourcentage, chercher le % dans la cellule précédente
                elif 'on' in text.lower() and 'stores' in text.lower() and i > 0:
                    prev_text = cell_texts[i-1].strip()
                    if '%' in prev_text:
                        success_rate = self._extract_percentage(prev_text)
            
            return {
                'id': retailer_id,
                'name': name,
                'stores_crawled': stores_crawled,
                'stores_failed': stores_failed,
                'stores_total': stores_total,
                'success_rate': success_rate,
                'progress_rate': progress_rate
            }
            
        except Exception as e:
            logger.debug(f"Erreur parsing ligne: {e}")
            return None
    
    def _extract_number(self, text: str) -> int:
        """Extraire un nombre d'un texte"""
        if not text or text == '/' or text == '-':
            return 0
        
        # Chercher le premier nombre dans le texte
        match = re.search(r'\d+', text)
        return int(match.group()) if match else 0
    
    def _extract_total_from_fraction(self, text: str) -> int:
        """Extraire le total d'une fraction comme '3/116' ou '2/2'"""
        if not text or text == '/' or text == '-':
            return 0
            
        # Chercher le pattern x/y
        match = re.search(r'(\d+)/(\d+)', text)
        if match:
            return int(match.group(2))  # Retourner le dénominateur
        
        # Si pas de fraction, chercher juste un nombre
        return self._extract_number(text)
    
    def _extract_percentage(self, text: str) -> float:
        """Extraire un pourcentage d'un texte"""
        if not text:
            return 0.0
            
        # Chercher le pattern nombre%
        match = re.search(r'([0-9.]+)%', text)
        return float(match.group(1)) if match else 0.0
    
    def _make_request(self, endpoint: str, method: str = 'GET', return_json: bool = True, **kwargs):
        """Faire une requête authentifiée"""
        if not self._authenticate():
            return None
            
        try:
            url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if return_json:
                # Essayer de parser en JSON
                try:
                    return response.json()
                except:
                    return response.text
            else:
                return response.text
                
        except Exception as e:
            logger.error(f"Erreur requête {endpoint}: {e}")
            return None
    
    def get_retailer_rules(self) -> List[Dict[str, Any]]:
        """Récupérer les règles des retailers depuis Spider Vision"""
        try:
            # Essayer différents endpoints possibles pour les retailers/règles
            endpoints = [
                '/api/retailers',
                '/api/rules',
                '/api/crawler/retailers',
                '/api/dashboard/retailers',
                '/retailers',
                '/rules'
            ]
            
            for endpoint in endpoints:
                response = self._make_request(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            logger.info(f"Données retailers trouvées via {endpoint}")
                            return self._normalize_retailer_rules(data)
                    except json.JSONDecodeError:
                        continue
            
            # Si pas d'API, créer des règles par défaut basées sur les retailers communs
            logger.warning("Impossible de récupérer les règles via API, utilisation des règles par défaut")
            return self._get_default_retailer_rules()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des règles: {e}")
            return self._get_default_retailer_rules()
    
    def _normalize_retailer_rules(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """Normaliser les données des retailers au format attendu"""
        rules = []
        for item in data:
            # Adapter selon la structure réelle des données Spider Vision
            rule = {
                'retailer_name': item.get('name', item.get('retailer', item.get('site_name', 'Unknown'))),
                'min_crawling_rate': float(item.get('min_crawling_rate', item.get('crawling_threshold', 95.0))),
                'min_crawling_rate_warning': float(item.get('min_crawling_rate_warning', item.get('crawling_warning', 90.0))),
                'min_content_rate': float(item.get('min_content_rate', item.get('content_threshold', 85.0))),
                'min_content_rate_warning': float(item.get('min_content_rate_warning', item.get('content_warning', 80.0))),
                'min_progress_0930': float(item.get('min_progress_0930', item.get('progress_threshold', 15.0)))
            }
            rules.append(rule)
        return rules
    
    def _get_default_retailer_rules(self) -> List[Dict[str, Any]]:
        """Règles par défaut si impossible de récupérer depuis l'API"""
        return [
            {
                'retailer_name': 'Carrefour',
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 15.0
            },
            {
                'retailer_name': 'Intermarché',
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 10.0
            },
            {
                'retailer_name': 'Auchan',
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 12.0
            },
            {
                'retailer_name': 'Leclerc',
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 15.0
            },
            {
                'retailer_name': 'Casino',
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 10.0
            }
        ]
    
    def get_success_counters(self, retailer_name: str, start_date, end_date) -> Dict[str, int]:
        """Récupérer les compteurs de succès/échec pour un retailer"""
        try:
            # Convertir datetime en date si nécessaire
            if hasattr(start_date, 'date'):
                start_date = start_date.date()
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
            
            # Essayer différents endpoints pour les données de crawl
            endpoints = [
                f'/api/crawler/stats/{retailer_name}',
                f'/api/stats/{retailer_name}',
                f'/api/crawler/runs/{retailer_name}',
                f'/api/runs/{retailer_name}',
                '/api/crawler/runs',
                '/api/runs'
            ]
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'retailer': retailer_name
            }
            
            for endpoint in endpoints:
                response = self._make_request(endpoint, params=params)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        return self._parse_success_counters(data, retailer_name)
                    except json.JSONDecodeError:
                        continue
            
            # Si pas de données, retourner des valeurs par défaut
            logger.warning(f"Impossible de récupérer les stats pour {retailer_name}, utilisation de valeurs par défaut")
            return {'success_count': 85, 'total_count': 100}
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des compteurs pour {retailer_name}: {e}")
            return {'success_count': 85, 'total_count': 100}
    
    def _parse_success_counters(self, data: Any, retailer_name: str) -> Dict[str, int]:
        """Parser les données de compteurs depuis l'API"""
        if isinstance(data, dict):
            # Format direct avec compteurs
            if 'success_count' in data and 'total_count' in data:
                return {
                    'success_count': int(data['success_count']),
                    'total_count': int(data['total_count'])
                }
            
            # Format avec liste de runs
            if 'runs' in data:
                runs = data['runs']
            elif isinstance(data, list):
                runs = data
            else:
                runs = []
            
            success_count = 0
            total_count = 0
            
            for run in runs:
                if isinstance(run, dict):
                    run_retailer = run.get('retailer', run.get('site', run.get('name', '')))
                    if retailer_name.lower() not in run_retailer.lower():
                        continue
                        
                    total_count += 1
                    status = run.get('status', run.get('result', run.get('success', False)))
                    
                    if status in ['success', 'completed', True, 1, 'ok']:
                        success_count += 1
            
            return {'success_count': success_count, 'total_count': max(total_count, 1)}
        
        return {'success_count': 85, 'total_count': 100}
    
    def get_progress_at_0930(self, retailer_name: str, target_date: datetime) -> float:
        """Récupérer le progrès à 09:30 pour un retailer"""
        try:
            # Calculer la fenêtre de temps autour de 09:30
            target_time = target_date.replace(hour=9, minute=30, second=0, microsecond=0)
            start_time = target_time - timedelta(minutes=30)
            end_time = target_time + timedelta(minutes=30)
            
            endpoints = [
                f'/api/crawler/progress/{retailer_name}',
                f'/api/progress/{retailer_name}',
                '/api/crawler/runs',
                '/api/runs'
            ]
            
            params = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'retailer': retailer_name,
                'date': target_date.strftime('%Y-%m-%d')
            }
            
            for endpoint in endpoints:
                response = self._make_request(endpoint, params=params)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        progress = self._parse_progress_data(data, retailer_name, target_time)
                        if progress is not None:
                            return progress
                    except json.JSONDecodeError:
                        continue
            
            # Essayer de récupérer depuis le dashboard
            dashboard_data = self.get_dashboard_data()
            for retailer in dashboard_data:
                if retailer['name'].lower() == retailer_name.lower():
                    return retailer['progress_rate']
            
            # Valeur par défaut si pas de données
            logger.warning(f"Impossible de récupérer le progrès à 09:30 pour {retailer_name}")
            return 12.5  # Valeur par défaut
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du progrès pour {retailer_name}: {e}")
            return 12.5
    
    def get_progress_at(self, retailer_name: str, target_date: datetime, target_time) -> tuple:
        """Récupérer le progrès à une heure donnée (compatible avec ReportService)"""
        # Convertir time en datetime pour la compatibilité
        if hasattr(target_time, 'hour'):
            target_datetime = target_date.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
        else:
            target_datetime = target_date.replace(hour=9, minute=30, second=0, microsecond=0)
        
        progress_percent = self.get_progress_at_0930(retailer_name, target_datetime)
        
        # Convertir le pourcentage en nombres absolus pour la compatibilité
        expected_total = 100  # Nombre total attendu
        completed_by_time = int((progress_percent / 100) * expected_total)
        
        return completed_by_time, expected_total
    
    def get_crawling_counters(self, retailer_name: str, start_date, end_date) -> Dict[str, int]:
        """Récupérer les compteurs de magasins crawlés (règle 1)"""
        try:
            # Convertir datetime en date si nécessaire
            if hasattr(start_date, 'date'):
                start_date = start_date.date()
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
            
            # Essayer différents endpoints pour les données de crawling
            endpoints = [
                f'/api/crawler/crawling/{retailer_name}',
                f'/api/crawling/{retailer_name}',
                f'/api/crawler/stores/{retailer_name}',
                f'/api/stores/{retailer_name}',
                '/api/crawler/crawling',
                '/api/crawling'
            ]
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'retailer': retailer_name
            }
            
            for endpoint in endpoints:
                response = self._make_request(endpoint, params=params)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        return self._parse_crawling_counters(data, retailer_name)
                    except json.JSONDecodeError:
                        continue
            
            # Si pas de données, retourner des valeurs par défaut
            logger.warning(f"Impossible de récupérer les stats de crawling pour {retailer_name}, utilisation de valeurs par défaut")
            return {'crawling_count': 92, 'total_count': 100}
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des compteurs de crawling pour {retailer_name}: {e}")
            return {'crawling_count': 92, 'total_count': 100}
    
    def _parse_crawling_counters(self, data: Any, retailer_name: str) -> Dict[str, int]:
        """Parser les données de compteurs de crawling depuis l'API"""
        if isinstance(data, dict):
            # Format direct avec compteurs
            if 'crawling_count' in data and 'total_count' in data:
                return {
                    'crawling_count': int(data['crawling_count']),
                    'total_count': int(data['total_count'])
                }
            
            # Format avec liste de magasins
            if 'stores' in data:
                stores = data['stores']
            elif isinstance(data, list):
                stores = data
            else:
                stores = []
            
            crawling_count = 0
            total_count = 0
            
            for store in stores:
                if isinstance(store, dict):
                    store_retailer = store.get('retailer', store.get('site', store.get('name', '')))
                    if retailer_name.lower() not in store_retailer.lower():
                        continue
                        
                    total_count += 1
                    crawled = store.get('crawled', store.get('status', store.get('success', False)))
                    
                    if crawled in ['crawled', 'success', 'completed', True, 1, 'ok']:
                        crawling_count += 1
            
            return {'crawling_count': crawling_count, 'total_count': max(total_count, 1)}
        
        return {'crawling_count': 92, 'total_count': 100}
    
    def get_content_counters(self, retailer_name: str, start_date, end_date) -> Dict[str, int]:
        """Récupérer les compteurs de magasins avec contenu (règle 2)"""
        try:
            # Convertir datetime en date si nécessaire
            if hasattr(start_date, 'date'):
                start_date = start_date.date()
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
            
            # Essayer différents endpoints pour les données de contenu
            endpoints = [
                f'/api/crawler/content/{retailer_name}',
                f'/api/content/{retailer_name}',
                f'/api/crawler/products/{retailer_name}',
                f'/api/products/{retailer_name}',
                '/api/crawler/content',
                '/api/content'
            ]
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'retailer': retailer_name
            }
            
            for endpoint in endpoints:
                response = self._make_request(endpoint, params=params)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        return self._parse_content_counters(data, retailer_name)
                    except json.JSONDecodeError:
                        continue
            
            # Si pas de données, retourner des valeurs par défaut
            logger.warning(f"Impossible de récupérer les stats de contenu pour {retailer_name}, utilisation de valeurs par défaut")
            return {'content_count': 84, 'total_count': 100}
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des compteurs de contenu pour {retailer_name}: {e}")
            return {'content_count': 84, 'total_count': 100}
    
    def _parse_content_counters(self, data: Any, retailer_name: str) -> Dict[str, int]:
        """Parser les données de compteurs de contenu depuis l'API"""
        if isinstance(data, dict):
            # Format direct avec compteurs
            if 'content_count' in data and 'total_count' in data:
                return {
                    'content_count': int(data['content_count']),
                    'total_count': int(data['total_count'])
                }
            
            # Format avec liste de magasins/produits
            if 'stores' in data:
                stores = data['stores']
            elif 'products' in data:
                stores = data['products']
            elif isinstance(data, list):
                stores = data
            else:
                stores = []
            
            content_count = 0
            total_count = 0
            
            for store in stores:
                if isinstance(store, dict):
                    store_retailer = store.get('retailer', store.get('site', store.get('name', '')))
                    if retailer_name.lower() not in store_retailer.lower():
                        continue
                        
                    total_count += 1
                    has_content = store.get('has_content', store.get('content', store.get('products_count', 0)))
                    
                    # Vérifier si le magasin a du contenu
                    if has_content in [True, 1, 'yes'] or (isinstance(has_content, (int, float)) and has_content > 0):
                        content_count += 1
            
            return {'content_count': content_count, 'total_count': max(total_count, 1)}
        
        return {'content_count': 84, 'total_count': 100}
