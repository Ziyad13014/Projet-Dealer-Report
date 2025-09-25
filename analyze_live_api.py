#!/usr/bin/env python3
"""
Script pour analyser les données Last day history directement via l'API SpiderVision
"""

import requests
import json
import ast
from typing import Dict, List, Any, Optional, Tuple
import os
from dotenv import load_dotenv

def get_token():
    """Récupère le token JWT depuis l'API"""
    load_dotenv()
    
    # Utiliser le token JWT pré-configuré
    existing_token = os.getenv('SPIDER_VISION_JWT_TOKEN')
    if existing_token:
        return existing_token
    
    # Fallback vers authentification
    from cli.services.auth import SpiderVisionAuth
    try:
        auth = SpiderVisionAuth()
        token = auth.login()
        return token
    except Exception as e:
        print(f"Erreur d'authentification: {e}")
        raise

def get_overview_data(token):
    """Récupère les données overview depuis l'API"""
    load_dotenv()
    url = os.getenv('SPIDER_VISION_API_BASE')
    overview_url = f"{url}/store-history/overview"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    response = requests.get(overview_url, headers=headers, timeout=30)
    response.raise_for_status()
    
    return response.json()

def parse_day_data(day_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse les données d'un jour pour extraire progress et successPercent"""
    if not day_str or day_str == "0":
        return None, None
    
    try:
        day_data = ast.literal_eval(day_str)
        if isinstance(day_data, dict):
            progress = day_data.get('progress')
            success_percent = day_data.get('successPercent')
            
            if isinstance(progress, str):
                progress = float(progress)
            
            return progress, success_percent
    except (ValueError, SyntaxError):
        pass
    
    return None, None

def apply_coherence_rule(values: List[float], max_deviation: float = 5.0) -> List[float]:
    """Applique la règle de cohérence : garde seulement les valeurs avec écart max ≤ 5%"""
    if len(values) <= 1:
        return values
    
    best_group = []
    
    for i in range(len(values)):
        current_group = [values[i]]
        
        for j in range(len(values)):
            if i != j:
                test_group = current_group + [values[j]]
                min_val = min(test_group)
                max_val = max(test_group)
                
                if max_val - min_val <= max_deviation:
                    current_group.append(values[j])
        
        if len(current_group) > len(best_group):
            best_group = current_group
    
    return best_group

def get_retailer_thresholds():
    """Retourne les seuils de succès minimum par enseigne basés sur le tableau de référence"""
    return {
        "Action": {"progress_min": 100.0, "success_min": 100.0},
        "Amazon": {"progress_min": 100.0, "success_min": 100.0},
        "Auchan": {"progress_min": 78.77, "success_min": 99.67},
        "Auchan Bi1": {"progress_min": None, "success_min": None},
        "Auchan Livraison": {"progress_min": 99.39, "success_min": 96.3},
        "Bi1 Drive": {"progress_min": 100.0, "success_min": 97.86},
        "Biocoop": {"progress_min": 100.0, "success_min": 99.57},
        "Bmstores": {"progress_min": None, "success_min": None},
        "Carrefour": {"progress_min": 48.98, "success_min": 99.28},
        "Casino": {"progress_min": None, "success_min": None},
        "Casino proximités": {"progress_min": 100.0, "success_min": 99.77},
        "ChronoDrive": {"progress_min": 98.25, "success_min": 100.0},
        "CollectAndGo": {"progress_min": 100.0, "success_min": 84.44},
        "Cora": {"progress_min": None, "success_min": None},
        "Deliveroo": {"progress_min": 100.0, "success_min": 97.84},
        "Eau-vive": {"progress_min": 100.0, "success_min": 100.0},
        "Franprix": {"progress_min": None, "success_min": None},
        "G20 Minute": {"progress_min": 100.0, "success_min": 100.0},
        "Greenweez": {"progress_min": 100.0, "success_min": 100.0},
        "Houra.fr": {"progress_min": 100.0, "success_min": 100.0},
        "Intermarché": {"progress_min": 13.02, "success_min": 99.85},
        "L'Oreal Paris": {"progress_min": 100.0, "success_min": 100.0},
        "La Belle Vie": {"progress_min": 100.0, "success_min": 100.0},
        "La Vie Claire": {"progress_min": 100.0, "success_min": 98.44},
        "Lafourche": {"progress_min": 100.0, "success_min": 100.0},
        "Leclerc": {"progress_min": 99.92, "success_min": 98.48},
        "MatchDrive": {"progress_min": 100.0, "success_min": 99.13},
        "Monoprix": {"progress_min": None, "success_min": None},
        "Monoprix plus": {"progress_min": 95.3, "success_min": 98.39},
        "Naturalia": {"progress_min": 100.0, "success_min": 100.0},
        "Picnic": {"progress_min": 100.0, "success_min": 100.0},
        "Satoriz": {"progress_min": 100.0, "success_min": 100.0},
        "Stokomani": {"progress_min": 100.0, "success_min": 100.0},
        "Système U": {"progress_min": 100.0, "success_min": 100.0},
        "Uber Eats": {"progress_min": 100.0, "success_min": 100.0}
    }

def get_status_for_retailer(value, threshold):
    """
    Détermine le statut basé sur la valeur et le seuil de l'enseigne
    - Succès: >= seuil
    - Warning: entre (seuil-5%) et (seuil-1%)  
    - Erreur: < (seuil-5%)
    """
    if threshold is None:
        return "N/A"
    
    if value >= threshold:
        return "Succès"
    elif value >= (threshold - 5.0):
        return "Warning"
    else:
        return "Erreur"

def analyze_retailer_history(retailer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse les données Last day history d'une enseigne avec les vraies données du site"""
    retailer_name = retailer_data.get('domainDealerName', 'Unknown')
    
    # Récupérer les seuils spécifiques pour cette enseigne
    retailer_thresholds = get_retailer_thresholds()
    thresholds = retailer_thresholds.get(retailer_name, {"progress_min": None, "success_min": None})
    
    # Analyser les vraies données du site
    progress_values = []
    success_values = []
    
    for day_key in ['day0', 'day1', 'day2', 'day3', 'day4', 'day5']:
        day_str = retailer_data.get(day_key, '')
        progress, success = parse_day_data(day_str)
        
        if progress is not None:
            progress_values.append(progress)
        if success is not None:
            success_values.append(success)
    
    # Appliquer la règle de cohérence (écart max ≤ 5%)
    coherent_progress = apply_coherence_rule(progress_values)
    coherent_success = apply_coherence_rule(success_values)
    
    # Calculer les moyennes
    avg_progress = sum(coherent_progress) / len(coherent_progress) if coherent_progress else 0.0
    avg_success = sum(coherent_success) / len(coherent_success) if coherent_success else 0.0
    
    # Déterminer les statuts avec les seuils spécifiques de l'enseigne
    progress_status = get_status_for_retailer(avg_progress, thresholds['progress_min'])
    success_status = get_status_for_retailer(avg_success, thresholds['success_min'])
    
    return {
        'retailer_name': retailer_name,
        'raw_progress': progress_values,
        'raw_success': success_values,
        'coherent_progress': coherent_progress,
        'coherent_success': coherent_success,
        'avg_progress': avg_progress,
        'avg_success': avg_success,
        'progress_status': progress_status,
        'success_status': success_status,
        'progress_threshold': thresholds['progress_min'],
        'success_threshold': thresholds['success_min']
    }

def main():
    """Fonction principale"""
    print("🔄 Récupération des données en direct depuis l'API SpiderVision...")
    
    try:
        # Authentification
        token = get_token()
        print("✅ Authentification réussie")
        
        # Récupération des données
        overview_data = get_overview_data(token)
        print("✅ Données récupérées avec succès")
        
        # Analyse des données
        print("\n📊 Analyse des Last day history avec règle de cohérence (écart max ≤ 5%)...")
        
        results = []
        # Vérifier si overview_data est une liste ou un dict
        if isinstance(overview_data, list):
            retailers_data = overview_data
        else:
            retailers_data = overview_data.get('data', [])
        
        for retailer_data in retailers_data:
            analysis = analyze_retailer_history(retailer_data)
            results.append(analysis)
        
        # Affichage du tableau
        print("\n" + "="*80)
        print("📋 TABLEAU FINAL - Analyse Last day history (DONNÉES EN DIRECT)")
        print("="*80)
        
        print(f"{'Enseigne':<25} {'Moy Prog':<10} {'Statut Prog':<12} {'Moy Succ':<10} {'Statut Succ':<12}")
        print("-"*80)
        
        success_count = {'progress': {'Succès': 0, 'Warning': 0, 'Erreur': 0, 'N/A': 0}, 
                        'success': {'Succès': 0, 'Warning': 0, 'Erreur': 0, 'N/A': 0}}
        
        for result in results:
            name = result['retailer_name'][:24]
            avg_prog = f"{result['avg_progress']:.1f}%"
            status_prog = result['progress_status']
            avg_succ = f"{result['avg_success']:.1f}%"
            status_succ = result['success_status']
            
            print(f"{name:<25} {avg_prog:<10} {status_prog:<12} {avg_succ:<10} {status_succ:<12}")
            
            success_count['progress'][status_prog] += 1
            success_count['success'][status_succ] += 1
        
        # Statistiques
        print("\n" + "="*60)
        print("📈 STATISTIQUES GLOBALES")
        print("="*60)
        
        print(f"\n🔵 Progression:")
        print(f"   ✅ Succès: {success_count['progress']['Succès']} enseignes")
        print(f"   ⚠️ Warning: {success_count['progress']['Warning']} enseignes")
        print(f"   ❌ Erreur: {success_count['progress']['Erreur']} enseignes")
        print(f"   🚫 N/A: {success_count['progress']['N/A']} enseignes")
        
        print(f"\n🟢 Succès Collecte:")
        print(f"   ✅ Succès: {success_count['success']['Succès']} enseignes")
        print(f"   ⚠️ Warning: {success_count['success']['Warning']} enseignes")
        print(f"   ❌ Erreur: {success_count['success']['Erreur']} enseignes")
        print(f"   🚫 N/A: {success_count['success']['N/A']} enseignes")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
