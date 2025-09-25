#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer un rapport HTML des données Last day history avec données réelles API
"""

import requests
import json
import ast
from typing import Dict, List, Any, Optional, Tuple
import os
from dotenv import load_dotenv
from datetime import datetime

def get_token():
    """Récupère le token JWT depuis l'API"""
    load_dotenv()
    
    url = os.getenv('SPIDER_VISION_URL')
    username = os.getenv('SPIDER_VISION_USERNAME')
    password = os.getenv('SPIDER_VISION_PASSWORD')
    
    # Essayer d'abord le token existant
    existing_token = os.getenv('SPIDER_VISION_JWT_TOKEN')
    if existing_token:
        return existing_token
    
    # Sinon, se connecter
    auth_url = f"{url}/auth/login"
    payload = {
        "email": username,
        "password": password
    }
    
    response = requests.post(auth_url, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    token = data.get('token') or data.get('access_token') or data.get('jwt') or data.get('accessToken')
    
    if not token:
        raise Exception(f"Token non trouvé dans la réponse: {data}")
    
    return token

def get_overview_data(token):
    """Récupère les données overview depuis l'API"""
    load_dotenv()
    url = os.getenv('SPIDER_VISION_URL')
    overview_url = f"{url}/overview"
    
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

def get_status_from_average(avg_value: float, baseline: float = 95.0, zero_days_count: int = 0) -> str:
    """Détermine le statut basé sur la moyenne et la baseline"""
    if avg_value is None:
        return "N/A"
    
    # Si 0% depuis 3+ jours, c'est une erreur critique
    if avg_value == 0 and zero_days_count >= 3:
        return "Erreur!"
    
    # Si 0% mais moins de 3 jours, erreur normale
    if avg_value == 0:
        return "Erreur"
    
    if avg_value >= baseline:
        return "Succès"
    elif avg_value >= (baseline - 5.0):
        return "Warning"
    else:
        return "Erreur"

def get_worst_status(status1: str, status2: str) -> str:
    """Retourne le pire statut entre deux statuts (priorité aux erreurs)"""
    status_priority = {
        "Erreur!": 4,
        "Erreur": 3,
        "Warning": 2,
        "Succès": 1,
        "N/A": 0
    }
    
    priority1 = status_priority.get(status1, 0)
    priority2 = status_priority.get(status2, 0)
    
    if priority1 >= priority2:
        return status1
    else:
        return status2

def create_progress_bar(percentage: float, status_class: str) -> str:
    """Crée une barre de progression HTML avec pourcentage"""
    # Limiter le pourcentage à 100% pour l'affichage visuel
    display_width = min(percentage, 100)
    
    return f"""<div class="progress-bar">
        <div class="progress-fill {status_class}" style="width: {display_width}%">{percentage:.1f}%</div>
    </div>"""

def analyze_retailer_history(retailer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse les données Last day history d'une enseigne avec données réelles"""
    retailer_name = retailer_data.get('domainDealerName', 'Unknown')
    
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
    
    # Déterminer les statuts avec les nouvelles règles simplifiées
    progress_status = get_status_from_average(avg_progress, 30.0)  # Baseline progression: 30%
    success_status = get_status_from_average(avg_success, 95.0)   # Baseline succès: 95%
    
    # Déterminer le statut global (le pire des deux)
    global_status = get_worst_status(progress_status, success_status)
    
    return {
        'retailer_name': retailer_name,
        'progress_avg': avg_progress,
        'progress_status': progress_status,
        'success_avg': avg_success,
        'success_status': success_status,
        'global_status': global_status
    }

def get_live_retailer_data():
    """Récupère les données réelles depuis l'API ou CSV de fallback"""
    print("🔄 Récupération des données en direct depuis l'API SpiderVision...")
    
    try:
        # Authentification
        token = get_token()
        print("✅ Authentification réussie")
        
        # Récupération des données
        overview_data = get_overview_data(token)
        print("✅ Données récupérées avec succès")
        
        # Analyse des données
        print("📊 Analyse des Last day history avec règle de cohérence (écart max ≤ 5%)...")
        
        retailer_data = {}
        retailers_data = overview_data.get('data', [])
        
        for retailer_raw_data in retailers_data:
            analysis = analyze_retailer_history(retailer_raw_data)
            retailer_data[analysis['retailer_name']] = {
                'progress_avg': analysis['progress_avg'],
                'progress_status': analysis['progress_status'],
                'success_avg': analysis['success_avg'],
                'success_status': analysis['success_status'],
                'global_status': analysis['global_status']
            }
        
        if not retailer_data:
            print("⚠️ Aucune donnée trouvée via API, utilisation du CSV de fallback...")
            return get_csv_fallback_data()
        
        return retailer_data
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données API: {e}")
        print("⚠️ Utilisation du CSV de fallback...")
        return get_csv_fallback_data()

def get_csv_fallback_data():
    """Récupère les données depuis le CSV local"""
    import csv
    
    try:
        csv_file = 'reports/spider_vision_overview_current.csv'
        retailer_data = {}
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                retailer_name = row.get('domainDealerName', '').strip()
                if not retailer_name or retailer_name == 'Unknown':
                    continue
                
                print(f"📊 Traitement de {retailer_name}")
                
                # Récupérer les métriques principales
                crawl_progress = row.get('crawlProgress', '').strip()
                crawl_success_progress = row.get('crawlSuccessProgress', '').strip()
                
                # Convertir en float si possible
                global_progress = 0.0
                success_rate = 0.0
                
                try:
                    if crawl_progress and crawl_progress != '':
                        global_progress = float(crawl_progress)
                        print(f"  📈 Global Progress: {global_progress}%")
                except (ValueError, TypeError):
                    pass
                
                try:
                    if crawl_success_progress and crawl_success_progress != '':
                        success_rate = float(crawl_success_progress)
                        print(f"  ✅ Success Rate: {success_rate}%")
                except (ValueError, TypeError):
                    pass
                
                # Si pas de données dans les colonnes principales, utiliser Last day history
                if global_progress == 0.0 and success_rate == 0.0:
                    progress_values = []
                    success_values = []
                    
                    for day_key in ['day0', 'day1', 'day2', 'day3', 'day4', 'day5']:
                        day_str = row.get(day_key, '').strip()
                        if day_str and day_str != '':
                            progress, success = parse_day_data(day_str)
                            
                            if progress is not None:
                                progress_values.append(progress)
                            if success is not None:
                                success_values.append(success)
                    
                    # Appliquer la règle de cohérence
                    coherent_progress = apply_coherence_rule(progress_values)
                    coherent_success = apply_coherence_rule(success_values)
                    
                    # Calculer les moyennes
                    global_progress = sum(coherent_progress) / len(coherent_progress) if coherent_progress else 0.0
                    success_rate = sum(coherent_success) / len(coherent_success) if coherent_success else 0.0
                    
                    print(f"  📊 Calculé depuis Last day history - Progress: {global_progress:.1f}%, Success: {success_rate:.1f}%")
                
                # Compter les jours à 0% pour déterminer si c'est une erreur critique
                progress_zero_days = sum(1 for val in progress_values if val == 0.0)
                success_zero_days = sum(1 for val in success_values if val == 0.0)
                
                # Déterminer les statuts selon les nouvelles règles
                progress_status = get_status_from_average(global_progress, 30.0, progress_zero_days)  # Baseline 30% pour progression
                success_status = get_status_from_average(success_rate, 95.0, success_zero_days)     # Baseline 95% pour succès
                
                # Déterminer le statut global (le pire des deux)
                global_status = get_worst_status(progress_status, success_status)
                
                print(f"  ✅ Statuts: Progress={global_progress:.1f}% ({progress_status}), Success={success_rate:.1f}% ({success_status}) → Global: {global_status}")
                
                retailer_data[retailer_name] = {
                    'progress_avg': global_progress,
                    'progress_status': progress_status,
                    'success_avg': success_rate,
                    'success_status': success_status,
                    'global_status': global_status
                }
        
        print(f"✅ Données extraites du CSV: {len(retailer_data)} enseignes")
        return retailer_data
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV: {e}")
        return {}

def get_status_class(status: str) -> str:
    """Retourne la classe CSS pour le statut"""
    if status == "Succès":
        return "success"
    elif status == "Warning":
        return "warning"
    elif status == "Erreur!":
        return "error-critical"
    elif status == "Erreur":
        return "error"
    else:
        return "na"

def generate_html_report():
    """Génère le rapport HTML avec données réelles API"""
    retailer_rules = get_live_retailer_data()
    current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
    
    # Calculer les statistiques
    stats = {
        'progress': {'Succès': 0, 'Warning': 0, 'Erreur': 0, 'Erreur!': 0, 'N/A': 0},
        'success': {'Succès': 0, 'Warning': 0, 'Erreur': 0, 'Erreur!': 0, 'N/A': 0},
        'global': {'Succès': 0, 'Warning': 0, 'Erreur': 0, 'Erreur!': 0, 'N/A': 0}
    }
    
    for retailer, data in retailer_rules.items():
        stats['progress'][data['progress_status']] += 1
        stats['success'][data['success_status']] += 1
        stats['global'][data['global_status']] += 1
    
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Last Day History - SpiderVision</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            order: 2;
        }}
        
        .table-container {{
            padding: 30px;
            overflow-x: auto;
            order: 1;
        }}
        
        .main-content {{
            display: flex;
            flex-direction: column;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
        }}
        
        .stat-card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .stat-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 8px 15px;
            border-radius: 5px;
        }}
        
        .stat-success {{ background: #d4edda; color: #155724; }}
        .stat-warning {{ background: #fff3cd; color: #856404; }}
        .status.error {{ background: #f8d7da; color: #721c24; }}
        .status.error-critical {{ background: #8b0000; color: white; }}
        .status.na {{ background: #e2e3e5; color: #383d41; }}
        
        /* Styles pour les jauges de progression */
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            margin: 5px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.8s ease-in-out;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 12px;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }}
        
        .progress-fill.success {{
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        }}
        
        .progress-fill.warning {{
            background: linear-gradient(90deg, #ffc107 0%, #fd7e14 100%);
            color: #212529;
            text-shadow: none;
        }}
        
        .progress-fill.error {{
            background: linear-gradient(90deg, #dc3545 0%, #e74c3c 100%);
        }}
        
        .progress-fill.error-critical {{
            background: linear-gradient(90deg, #8b0000 0%, #dc143c 100%);
        }}
        
        .progress-fill.na {{
            background: linear-gradient(90deg, #6c757d 0%, #495057 100%);
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        /* Detail button */
        .detail-btn {{
            padding: 8px 14px;
            border-radius: 20px;
            border: 1px solid #4a5568;
            background: #374151;
            color: #fff;
            cursor: pointer;
            font-weight: 600;
            transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
        }}
        .detail-btn:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px rgba(0,0,0,.25); }}
        /* Modal */
        .modal-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,.6); display: none; align-items: center; justify-content: center; z-index: 1000; }}
        .modal {{ background: #111827; color: #fff; width: min(720px, 92vw); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,.5); border: 1px solid #374151; }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid #374151; }}
        .modal-title {{ font-size: 18px; font-weight: 700; }}
        .modal-close {{ background: transparent; border: none; color: #9ca3af; font-size: 22px; cursor: pointer; }}
        .modal-close:hover {{ color: #fff; }}
        .modal-body {{ padding: 18px; display: grid; gap: 12px; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 9999px; font-size: 12px; font-weight: 700; margin-left: 6px; }}
        .badge.success {{ background: #10b981; color: #06251d; }}
        .badge.warning {{ background: #fbbf24; color: #3a2d04; }}
        .badge.error {{ background: #ef4444; color: #3c0d0d; }}
        .badge.error-critical {{ background: #8b0000; color: #fff; }}
        .kv {{ display: grid; grid-template-columns: 160px 1fr; align-items: center; gap: 8px; }}
        .kv > div:first-child {{ color: #9ca3af; font-size: 13px; }}
        .intro-list {{ margin-top: 6px; margin-left: 18px; color: #9ca3af; }}
        .history-day {{ display: inline-block; width: 30px; height: 20px; margin: 2px; border-radius: 3px; text-align: center; font-size: 10px; line-height: 20px; color: white; }}
        .history-success {{ background: #10b981; }}
        .history-warning {{ background: #f59e0b; }}
        .history-error {{ background: #ef4444; }}
        .history-na {{ background: #6b7280; }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .filter-btn.active {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .btn-all {{ background: #6c757d; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: #212529; }}
        .btn-error {{ background: #dc3545; color: white; }}
        .btn-error-critical {{ background: #8b0000; color: white; }}
        .btn-na {{ background: #6c757d; color: white; }}
        
        .hidden {{
            display: none !important;
        }}
        
        .info-icon {{
            font-size: 0.8em;
            margin-left: 5px;
            cursor: help;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }}
        
        .info-icon:hover {{
            opacity: 1;
        }}
        
        /* Tooltip styling */
        .info-icon[title] {{
            position: relative;
        }}
        
        .info-icon[title]:hover::after {{
            content: attr(title);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        
        .info-icon[title]:hover::before {{
            content: '';
            position: absolute;
            bottom: 95%;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #333;
            z-index: 1000;
        }}
        
        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        th {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 500;
            border: 2px solid #2c3e50;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
            border: 2px solid transparent;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .enseigne-col {{
            font-weight: 600;
            color: #2c3e50;
            border-left: 2px solid #2c3e50 !important;
            border-right: 2px solid #2c3e50 !important;
            background: white !important;
        }}
        
        .status-success {{ background: #d4edda !important; color: #155724; }}
        .status-warning {{ background: #fff3cd !important; color: #856404; }}
        .status-error {{ background: #f8d7da !important; color: #721c24; }}
        .status-na {{ background: #e2e3e5 !important; color: #383d41; }}
        
        .percentage {{
            font-weight: 600;
            font-size: 1.1em;
        }}
        
        .hidden {{ display: none; }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .filter-buttons {{ justify-content: center; }}
            table {{ font-size: 0.9em; }}
        }}
        
        .status.error-critical {{ background: #8b0000; color: white; }}
        .status.na {{ background: #e2e3e5; color: #383d41; }}
        
        /* Styles pour les jauges de progression */
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            margin: 5px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.8s ease-in-out;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 12px;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }}
        
        .progress-fill.success {{
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        }}
        
        .progress-fill.warning {{
            background: linear-gradient(90deg, #ffc107 0%, #fd7e14 100%);
            color: #212529;
            text-shadow: none;
        }}
        
        .progress-fill.error {{
            background: linear-gradient(90deg, #dc3545 0%, #e74c3c 100%);
        }}
        
        .progress-fill.error-critical {{
            background: linear-gradient(90deg, #8b0000 0%, #dc143c 100%);
        }}
        
        .progress-fill.na {{
            background: linear-gradient(90deg, #6c757d 0%, #495057 100%);
        }}
        
        .progress-text {{
            position: absolute;
            width: 100%;
            text-align: center;
            font-weight: 600;
            font-size: 12px;
            color: #495057;
            z-index: 2;
        }}
        
        .stats {{
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rapport Last Day History</h1>
            <p>Analyse des performances SpiderVision - Généré le {current_time}</p>
        </div>
        
        <div class="filters">
            <div class="filter-buttons">
                <button class="filter-btn btn-all active" onclick="filterTable('all', this)">Toutes ({sum(stats['global'].values())})</button>
                <button class="filter-btn btn-success" onclick="filterTable('success', this)">Succès ({stats['global']['Succès']})</button>
                <button class="filter-btn btn-warning" onclick="filterTable('warning', this)">Warning ({stats['global']['Warning']})</button>
                <button class="filter-btn btn-error" onclick="filterTable('error', this)">Erreur ({stats['global']['Erreur']})</button>
                <button class="filter-btn btn-error-critical" onclick="filterTable('error-critical', this)">Erreur! ({stats['global']['Erreur!']})</button>
                <button class="filter-btn btn-na" onclick="filterTable('na', this)">N/A ({stats['global']['N/A']})</button>
            </div>
        </div>
        
        <div class="table-container">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Enseigne</th>
                        <th>
                            Global Progress (%)
                            <span class="info-icon" title="Pourcentage du crawler qui a réussi (barre bleue foncé dans l'interface SpiderVision)">ℹ️</span>
                        </th>
                        <th>
                            Statut Progress
                            <span class="info-icon" title="Succès: ≥30% | Warning: 25-30% | Erreur: <25%">ℹ️</span>
                        </th>
                        <th>
                            Success Rate (%)
                            <span class="info-icon" title="Pourcentage des magasins crawlés parfaitement (colonne Success dans SpiderVision)">ℹ️</span>
                        </th>
                        <th>
                            Statut Success
                            <span class="info-icon" title="Succès: ≥95% | Warning: 90-95% | Erreur: <90%">ℹ️</span>
                        </th>
                        <th>
                            Statut Global
                            <span class="info-icon" title="Pire statut entre Progress et Success">ℹ️</span>
                        </th>
                        <th>Détail</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Construire une map d'historique (successPercent day0..day5) depuis le CSV pour alimenter le bouton Détail
    history_map = {}
    try:
        import csv as _csv
        with open('reports/spider_vision_overview_current.csv', 'r', encoding='utf-8') as _f:
            _reader = _csv.DictReader(_f)
            for _row in _reader:
                _name = (_row.get('domainDealerName') or '').strip()
                if not _name:
                    continue
                _hist = []
                for _i in range(6):
                    _k = f'day{_i}'
                    _v = _row.get(_k, '')
                    if _v:
                        try:
                            _d = ast.literal_eval(_v)
                            _hist.append(_d.get('successPercent'))
                        except Exception:
                            _hist.append(None)
                    else:
                        _hist.append(None)
                history_map[_name] = _hist
    except Exception:
        history_map = {}

    # Générer les lignes du tableau
    table_rows = ""
    for retailer, data in sorted(retailer_rules.items()):
        # Texte statut global et classe
        global_status_text = data['global_status']
        name_attr = retailer.replace('"', '&quot;')
        history_json = json.dumps(history_map.get(retailer, []))
        
        table_rows += f"""
                    <tr data-global-status="{global_status_text}">
                        <td><strong>{retailer}</strong></td>
                        <td>{create_progress_bar(data['progress_avg'], get_status_class(data['progress_status']))}</td>
                        <td><span class="status {get_status_class(data['progress_status'])}">{data['progress_status']}</span></td>
                        <td>{create_progress_bar(data['success_avg'], get_status_class(data['success_status']))}</td>
                        <td><span class="status {get_status_class(data['success_status'])}">{data['success_status']}</span></td>
                        <td><span class="status {get_status_class(global_status_text)}">{global_status_text}</span></td>
                        <td>
                            <button class="detail-btn" onclick="openDetailFromButton(this)"
                                data-name="{name_attr}"
                                data-progress="{data['progress_avg']}"
                                data-progress-status="{data['progress_status']}"
                                data-success="{data['success_avg']}"
                                data-success-status="{data['success_status']}"
                                data-history='{history_json}'>
                                {global_status_text}
                            </button>
                        </td>
                    </tr>"""
    
    html_content += table_rows + """
                </tbody>
            </table>
        </div>
        
        <!-- Modal for Details -->
        <div id="detailModal" class="modal-overlay">
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title" id="modalTitle">Détails</div>
                    <button class="modal-close" id="modalClose" aria-label="Fermer">×</button>
                </div>
                <div class="modal-body">
                    <div class="detail-intro">
                        Voici ce que contient cette fiche détail :
                        <ul class="intro-list">
                            <li>Statut global de l'enseigne</li>
                            <li>Progress & Success du jour (avec badges)</li>
                            <li>Historique des 6 derniers jours (Success %)</li>
                        </ul>
                    </div>
                    <div class="kv"><div>Enseigne</div><div id="mName">-</div></div>
                    <div class="kv"><div>Progress</div><div id="mProgress">—</div></div>
                    <div class="kv"><div>Success</div><div id="mSuccess">—</div></div>
                    <div class="legend"><span class="badge success">Succès</span> <span class="badge warning">Warning</span> <span class="badge error">Erreur</span> <span class="badge error-critical">Erreur!</span></div>
                    <div class="history" id="mHistory"></div>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🔵 Progression (Crawling)</h3>
                <div class="stat-item stat-success">
                    <span>✅ Succès</span>
                    <strong>{stats['progress']['Succès']}</strong>
                </div>
                <div class="stat-item stat-warning">
                    <span>⚠️ Warning</span>
                    <strong>{stats['progress']['Warning']}</strong>
                </div>
                <div class="stat-item stat-error">
                    <span>❌ Erreur</span>
                    <strong>{stats['progress']['Erreur']}</strong>
                </div>
                <div class="stat-item stat-na">
                    <span>🚫 N/A</span>
                    <strong>{stats['progress']['N/A']}</strong>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>🟢 Succès Collecte</h3>
                <div class="stat-item stat-success">
                    <span>✅ Succès</span>
                    <strong>{stats['success']['Succès']}</strong>
                </div>
                <div class="stat-item stat-warning">
                    <span>⚠️ Warning</span>
                    <strong>{stats['success']['Warning']}</strong>
                </div>
                <div class="stat-item stat-error">
                    <span>❌ Erreur</span>
                    <strong>{stats['success']['Erreur']}</strong>
                </div>
                <div class="stat-item stat-na">
                    <span>🚫 N/A</span>
                    <strong>{stats['success']['N/A']}</strong>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>📊 Statut Global</h3>
                <div class="stat-item stat-success">
                    <span>✅ Succès</span>
                    <strong>{stats['global']['Succès']}</strong>
                </div>
                <div class="stat-item stat-warning">
                    <span>⚠️ Warning</span>
                    <strong>{stats['global']['Warning']}</strong>
                </div>
                <div class="stat-item stat-error">
                    <span>❌ Erreur</span>
                    <strong>{stats['global']['Erreur']}</strong>
                </div>
                <div class="stat-item stat-error-critical">
                    <span>❌ Erreur!</span>
                    <strong>{stats['global']['Erreur!']}</strong>
                </div>
                <div class="stat-item stat-na">
                    <span>🚫 N/A</span>
                    <strong>{stats['global']['N/A']}</strong>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function getStatusClass(status) {
            if (status === 'Succès') return 'success';
            if (status === 'Warning') return 'warning';
            if (status === 'Erreur!') return 'error-critical';
            if (status === 'Erreur') return 'error';
            if (status === 'N/A') return 'na';
            return '';
        }
        function filterTable(filter, el) {
            const rows = document.querySelectorAll('#dataTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            if (el) { el.classList.add('active'); }
            rows.forEach(row => {
                const status = row.getAttribute('data-global-status');
                const cls = getStatusClass(status);
                if (filter === 'all' || filter === cls || (filter === 'error-critical' && status === 'Erreur!')) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        // Detail modal interactions
        const modal = document.getElementById('detailModal');
        const modalClose = document.getElementById('modalClose');
        const mTitle = document.getElementById('modalTitle');
        const mName = document.getElementById('mName');
        const mProgress = document.getElementById('mProgress');
        const mSuccess = document.getElementById('mSuccess');
        const mHistory = document.getElementById('mHistory');
        function badge(statusText) {
            const cls = getStatusClass(statusText);
            return `<span class="badge ${cls}">${statusText}</span>`;
        }
        function fillDetailFromBtn(btn) {
            const name = btn.getAttribute('data-name') || '';
            const progress = parseFloat(btn.getAttribute('data-progress') || '0');
            const success = parseFloat(btn.getAttribute('data-success') || '0');
            const progressStatus = btn.getAttribute('data-progress-status') || '';
            const successStatus = btn.getAttribute('data-success-status') || '';
            let history = [];
            try {
                const raw = btn.getAttribute('data-history');
                if (raw) { history = JSON.parse(raw); }
            } catch (err) { history = []; }
            mTitle.textContent = `Détails - ${name}`;
            mName.textContent = name || '—';
            mProgress.innerHTML = `${isFinite(progress) ? progress.toFixed(1) : '—'}% ${badge(progressStatus)}`;
            mSuccess.innerHTML = `${isFinite(success) ? success.toFixed(1) : '—'}% ${badge(successStatus)}`;
            if (Array.isArray(history) && history.filter(v => v !== null && v !== undefined).length) {
                const items = history.map((v, idx) => v == null ? `<li>Jour -${idx}: n/a</li>` : `<li>Jour -${idx}: ${Number(v).toFixed(1)}%</li>`).join('');
                mHistory.innerHTML = `<h4>Historique Success (6 jours)</h4><ul>${items}</ul>`;
            } else {
                const days = ['J-5','J-4','J-3','J-2','J-1','J-0'];
                const boxes = days.map(d => `<span class=\"history-day history-na\" title=\"${d}\">${d.replace('J-','-')}</span>`).join('');
                mHistory.innerHTML = `<h4>Historique (6 jours)</h4><div>${boxes}</div><div style=\"margin-top:6px;color:#9ca3af;font-size:12px;\">Les valeurs s'afficheront ici dès que l'historique sera disponible.</div>`;
            }
        }
        let lastDetailBtn = null;
        function openDetailFromButton(btn) {
            fillDetailFromBtn(btn);
            // Update button label to show a text as requested
            if (!btn.getAttribute('data-original-label')) {
                btn.setAttribute('data-original-label', btn.textContent.trim());
            }
            btn.textContent = 'Détails affichés';
            lastDetailBtn = btn;
            modal.style.display = 'flex';
        }
        function closeModal() { 
            modal.style.display = 'none'; 
            if (lastDetailBtn) {
                const original = lastDetailBtn.getAttribute('data-original-label');
                if (original) lastDetailBtn.textContent = original;
                lastDetailBtn = null;
            }
        }
        if (modalClose) modalClose.addEventListener('click', closeModal);
        if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
        // Animation d'entrée
        document.addEventListener('DOMContentLoaded', function() {
            const rows = document.querySelectorAll('#dataTable tbody tr');
            rows.forEach((row, index) => {
                row.style.opacity = '0';
                row.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    row.style.transition = 'all 0.3s ease';
                    row.style.opacity = '1';
                    row.style.transform = 'translateY(0)';
                }, index * 50);
            });
        });
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """Fonction principale"""
    print("🔄 Génération du rapport HTML Last Day History avec données réelles API...")
    
    html_content = generate_html_report()
    
    # Générer le nom de fichier avec date et heure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'reports/last_day_history_live_report_{timestamp}.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Rapport généré avec succès: {output_file}")
    print(f"📊 Ouvrez le fichier dans votre navigateur pour voir le rapport interactif avec données réelles")

if __name__ == "__main__":
    main()
