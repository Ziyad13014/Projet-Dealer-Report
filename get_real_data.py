#!/usr/bin/env python3
"""
Script pour récupérer les données en direct depuis l'API SpiderVision
"""

import os
import json
import ast
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from dotenv import load_dotenv

# Import des modules existants
from cli.services.auth import SpiderVisionAuth
from cli.services.data import SpiderVisionData

def parse_day_data(day_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse les données d'un jour pour extraire progress et successPercent"""
    if not day_str or day_str == "0":
        return None, None
    
    try:
        # Essayer d'évaluer comme dictionnaire Python
        day_data = ast.literal_eval(day_str)
        if isinstance(day_data, dict):
            progress = day_data.get('progress')
            success_percent = day_data.get('successPercent')
            
            # Convertir progress en float si c'est une string
            if isinstance(progress, str):
                progress = float(progress)
            
            return progress, success_percent
    except (ValueError, SyntaxError):
        pass
    
    return None, None

def apply_coherence_rule(values: List[float], max_deviation: float = 5.0) -> List[float]:
    """Applique la règle de cohérence : garde seulement les valeurs avec écart max ≤ max_deviation%"""
    if len(values) <= 1:
        return values
    
    # Tester tous les groupes possibles de valeurs cohérentes
    best_group = []
    
    for i in range(len(values)):
        current_group = [values[i]]
        
        for j in range(len(values)):
            if i != j:
                # Vérifier si cette valeur est cohérente avec le groupe actuel
                test_group = current_group + [values[j]]
                min_val = min(test_group)
                max_val = max(test_group)
                
                if max_val - min_val <= max_deviation:
                    current_group.append(values[j])
        
        # Garder le plus grand groupe cohérent
        if len(current_group) > len(best_group):
            best_group = current_group
    
    return best_group

def analyze_retailer_history(retailer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse les données Last day history d'une enseigne"""
    retailer_name = retailer_data.get('domainDealerName', 'Unknown')
    
    # Extraire les données des 6 derniers jours
    progress_values = []
    success_values = []
    
    for day_key in ['day0', 'day1', 'day2', 'day3', 'day4', 'day5']:
        day_str = retailer_data.get(day_key, '')
        progress, success = parse_day_data(day_str)
        
        if progress is not None:
            progress_values.append(progress)
        if success is not None:
            success_values.append(success)
    
    # Appliquer la règle de cohérence
    coherent_progress = apply_coherence_rule(progress_values)
    coherent_success = apply_coherence_rule(success_values)
    
    # Calculer les moyennes
    avg_progress = sum(coherent_progress) / len(coherent_progress) if coherent_progress else 0.0
    avg_success = sum(coherent_success) / len(coherent_success) if coherent_success else 0.0
    
    # Déterminer les statuts
    def get_progress_status(value):
        if value >= 30:
            return "Succès"
        elif value >= 10:
            return "Warning"
        else:
            return "Erreur"
    
    def get_success_status(value):
        if value >= 90:
            return "Succès"
        elif value >= 50:
            return "Warning"
        else:
            return "Erreur"
    
    return {
        'retailer_name': retailer_name,
        'raw_progress': progress_values,
        'raw_success': success_values,
        'coherent_progress': coherent_progress,
        'coherent_success': coherent_success,
        'avg_progress': avg_progress,
        'avg_success': avg_success,
        'progress_status': get_progress_status(avg_progress),
        'success_status': get_success_status(avg_success)
    }

def main():
    """Fonction principale"""
    load_dotenv()
    
    print("🔄 Récupération des données en direct depuis l'API SpiderVision...")
    
    # Authentification
    auth = SpiderVisionAuth()
    try:
        token = auth.login()
        print("✅ Authentification réussie")
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        return
    
    # Récupération des données
    data_service = SpiderVisionData()
    try:
        overview_data = data_service.get_overview(token)
        print("✅ Données récupérées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {e}")
        return
    
    # Analyse des données
    print("\n📊 Analyse des Last day history avec règle de cohérence (écart max ≤ 5%)...")
    
    results = []
    retailers_data = overview_data.get('data', [])
    
    for retailer_data in retailers_data:
        analysis = analyze_retailer_history(retailer_data)
        results.append(analysis)
    
    # Affichage du tableau
    print("\n" + "="*100)
    print("📋 TABLEAU FINAL - Analyse Last day history (DONNÉES EN DIRECT)")
    print("="*100)
    
    print(f"{'Enseigne':<25} {'Moy Prog':<10} {'Statut Prog':<12} {'Moy Succ':<10} {'Statut Succ':<12}")
    print("-"*100)
    
    success_count = {'progress': {'Succès': 0, 'Warning': 0, 'Erreur': 0}, 
                    'success': {'Succès': 0, 'Warning': 0, 'Erreur': 0}}
    
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
    
    print(f"\n🟢 Succès Collecte:")
    print(f"   ✅ Succès: {success_count['success']['Succès']} enseignes")
    print(f"   ⚠️ Warning: {success_count['success']['Warning']} enseignes")
    print(f"   ❌ Erreur: {success_count['success']['Erreur']} enseignes")

if __name__ == "__main__":
    main()
