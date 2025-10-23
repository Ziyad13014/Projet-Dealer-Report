"""Repository avec des données mock pour tester le projet dealer-report."""
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import random

logger = logging.getLogger(__name__)

class MockDataRepository:
    """Repository avec des données simulées réalistes."""
    
    def __init__(self):
        self.retailers = [
            'Carrefour', 'Intermarché', 'Auchan', 'Leclerc', 'Casino',
            'Monoprix', 'Franprix', 'Super U', 'Hyper U', 'Cora'
        ]
        
    def get_rules(self, dealer_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupérer les règles des retailers avec seuils pour succès/warning/erreur."""
        rules = [
            {
                'retailer_name': 'Carrefour', 
                'min_crawling_rate': 95.0,  # Seuil de succès pour % magasins crawlés
                'min_crawling_rate_warning': 90.0,  # Seuil d'avertissement
                'min_content_rate': 85.0,  # Seuil de succès pour % magasins avec contenu
                'min_content_rate_warning': 80.0,  # Seuil d'avertissement
                'min_progress_0930': 15.0  # Garde l'ancien pour compatibilité
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
            },
            {
                'retailer_name': 'Monoprix', 
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 8.0
            },
            {
                'retailer_name': 'Franprix', 
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 9.0
            },
            {
                'retailer_name': 'Super U', 
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 11.0
            },
            {
                'retailer_name': 'Hyper U', 
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 10.0
            },
            {
                'retailer_name': 'Cora', 
                'min_crawling_rate': 95.0,
                'min_crawling_rate_warning': 90.0,
                'min_content_rate': 85.0,
                'min_content_rate_warning': 80.0,
                'min_progress_0930': 9.0
            }
        ]
        
        if dealer_filter:
            rules = [r for r in rules if dealer_filter.lower() in r['retailer_name'].lower()]
            
        logger.info(f"Retour de {len(rules)} règles (filtre: {dealer_filter})")
        return rules
    
    def get_success_counters(self, retailer_name: str, start_date, end_date) -> Dict[str, int]:
        """Générer des compteurs de succès/échec simulés."""
        # Convertir en date si nécessaire
        if hasattr(start_date, 'date'):
            start_date = start_date.date()
        if hasattr(end_date, 'date'):
            end_date = end_date.date()
            
        # Simuler des données réalistes
        days = (end_date - start_date).days + 1
        base_runs_per_day = random.randint(80, 120)
        total_runs = base_runs_per_day * days
        
        # Simuler un taux de succès variable selon le retailer
        success_rates = {
            'Carrefour': 0.96,
            'Intermarché': 0.88,
            'Auchan': 0.94,
            'Leclerc': 0.95,
            'Casino': 0.85,
            'Monoprix': 0.82,
            'Franprix': 0.84,
            'Super U': 0.92,
            'Hyper U': 0.90,
            'Cora': 0.83
        }
        
        base_rate = success_rates.get(retailer_name, 0.90)
        # Ajouter un peu de variabilité
        actual_rate = base_rate + random.uniform(-0.05, 0.05)
        actual_rate = max(0.0, min(1.0, actual_rate))
        
        success_count = int(total_runs * actual_rate)
        
        logger.info(f"Compteurs pour {retailer_name}: {success_count}/{total_runs} ({actual_rate:.1%})")
        
        return {
            'success_count': success_count,
            'total_count': total_runs
        }
    
    def get_crawling_counters(self, retailer_name: str, start_date, end_date) -> Dict[str, int]:
        """Générer des compteurs de magasins crawlés (règle 1)."""
        # Convertir en date si nécessaire
        if hasattr(start_date, 'date'):
            start_date = start_date.date()
        if hasattr(end_date, 'date'):
            end_date = end_date.date()
            
        # Simuler des données réalistes pour le crawling
        days = (end_date - start_date).days + 1
        base_stores_per_day = random.randint(80, 120)
        total_count = base_stores_per_day * days
        
        # Simuler un taux de crawling variable selon le retailer
        crawling_rates = {
            'Carrefour': 0.96,
            'Intermarché': 0.91,
            'Auchan': 0.94,
            'Leclerc': 0.97,
            'Casino': 0.88,
            'Monoprix': 0.85,
            'Franprix': 0.87,
            'Super U': 0.93,
            'Hyper U': 0.90,
            'Cora': 0.86
        }
        
        base_rate = crawling_rates.get(retailer_name, 0.90)
        # Ajouter un peu de variabilité
        actual_rate = base_rate + random.uniform(-0.03, 0.03)
        actual_rate = max(0.0, min(1.0, actual_rate))
        
        crawling_count = int(total_count * actual_rate)
        
        logger.info(f"Crawling pour {retailer_name}: {crawling_count}/{total_count} ({actual_rate:.1%})")
        
        return {
            'crawling_count': crawling_count,
            'total_count': total_count
        }
    
    def get_content_counters(self, retailer_name: str, start_date, end_date) -> Dict[str, int]:
        """Générer des compteurs de magasins avec contenu (règle 2)."""
        # Convertir en date si nécessaire
        if hasattr(start_date, 'date'):
            start_date = start_date.date()
        if hasattr(end_date, 'date'):
            end_date = end_date.date()
            
        # Simuler des données réalistes pour le contenu
        days = (end_date - start_date).days + 1
        base_stores_per_day = random.randint(80, 120)
        total_count = base_stores_per_day * days
        
        # Simuler un taux de contenu variable selon le retailer (généralement plus bas que le crawling)
        content_rates = {
            'Carrefour': 0.88,
            'Intermarché': 0.82,
            'Auchan': 0.86,
            'Leclerc': 0.89,
            'Casino': 0.78,
            'Monoprix': 0.75,
            'Franprix': 0.79,
            'Super U': 0.84,
            'Hyper U': 0.81,
            'Cora': 0.77
        }
        
        base_rate = content_rates.get(retailer_name, 0.80)
        # Ajouter un peu de variabilité
        actual_rate = base_rate + random.uniform(-0.05, 0.05)
        actual_rate = max(0.0, min(1.0, actual_rate))
        
        content_count = int(total_count * actual_rate)
        
        logger.info(f"Contenu pour {retailer_name}: {content_count}/{total_count} ({actual_rate:.1%})")
        
        return {
            'content_count': content_count,
            'total_count': total_count
        }
    
    def get_progress_at(self, retailer_name: str, target_date, target_time) -> tuple:
        """Simuler le progrès à une heure donnée."""
        # Convertir en date si nécessaire
        if hasattr(target_date, 'date'):
            target_date = target_date.date()
            
        # Simuler des données de progrès
        expected_total = 100
        
        # Simuler un progrès variable selon le retailer et l'heure
        progress_rates = {
            'Carrefour': 0.18,
            'Intermarché': 0.08,
            'Auchan': 0.14,
            'Leclerc': 0.16,
            'Casino': 0.07,
            'Monoprix': 0.06,
            'Franprix': 0.08,
            'Super U': 0.12,
            'Hyper U': 0.11,
            'Cora': 0.08
        }
        
        base_progress = progress_rates.get(retailer_name, 0.10)
        # Ajouter de la variabilité
        actual_progress = base_progress + random.uniform(-0.03, 0.03)
        actual_progress = max(0.0, min(1.0, actual_progress))
        
        completed_by_time = int(expected_total * actual_progress)
        
        logger.info(f"Progrès pour {retailer_name} à 09:30: {completed_by_time}/{expected_total} ({actual_progress:.1%})")
        
        return completed_by_time, expected_total
