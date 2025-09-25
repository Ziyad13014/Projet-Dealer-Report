#!/usr/bin/env python3
"""
Script pour générer immédiatement un rapport avec timestamp actuel
"""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv

def create_progress_bar(percentage, status_class):
    """Crée une barre de progression HTML"""
    display_width = min(percentage, 100)
    return f"""<div class="progress-bar">
        <div class="progress-fill {status_class}" style="width: {display_width}%">{percentage:.1f}%</div>
    </div>"""

def create_stacked_progress_bars(progress_val, progress_status, success_val, success_status):
    """Crée deux barres de progression empilées avec couleurs distinctes"""
    progress_width = min(progress_val, 100)
    success_width = min(success_val, 100)
    
    # Couleurs fixes pour différencier Progress (bleu) et Success (vert)
    progress_color = "progress-blue"
    success_color = "success-green"
    
    return f"""<div class="stacked-bars">
        <div class="progress-bar-small">
            <div class="progress-fill {progress_color}" style="width: {progress_width}%">{progress_val:.1f}%</div>
        </div>
        <div class="progress-bar-small">
            <div class="progress-fill {success_color}" style="width: {success_width}%">{success_val:.1f}%</div>
        </div>
    </div>"""

def get_status_class(status):
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

def get_worst_status(status1, status2):
    """Retourne le pire statut entre deux"""
    status_priority = {
        "Erreur!": 4,
        "Erreur": 3,
        "Warning": 2,
        "Succès": 1,
        "N/A": 0
    }
    
    priority1 = status_priority.get(status1, 0)
    priority2 = status_priority.get(status2, 0)
    
    return status1 if priority1 >= priority2 else status2

def get_status_from_value(value, baseline):
    """Détermine le statut basé sur la valeur et baseline"""
    if value == 0:
        return "Erreur!"
    elif value >= baseline:
        return "Succès"
    elif value >= (baseline - 5.0):
        return "Warning"
    else:
        return "Erreur"

def generate_report_now():
    """Génère un rapport immédiatement avec les données CSV"""
    print("🔄 Génération rapport en cours...")
    
    # Lire le CSV
    csv_file = 'reports/spider_vision_overview_current.csv'
    retailers_data = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                retailer_name = row.get('domainDealerName', '').strip()
                if not retailer_name:
                    continue
                
                # Extraire les métriques
                progress = float(row.get('crawlProgress', 0) or 0)
                success = float(row.get('crawlSuccessProgress', 0) or 0)
                
                # Déterminer les statuts
                progress_status = get_status_from_value(progress, 30.0)
                success_status = get_status_from_value(success, 95.0)
                global_status = get_worst_status(progress_status, success_status)
                
                retailers_data.append({
                    'name': retailer_name,
                    'progress': progress,
                    'progress_status': progress_status,
                    'success': success,
                    'success_status': success_status,
                    'global_status': global_status
                })
        
        print(f"✅ {len(retailers_data)} retailers traités")
        
    except Exception as e:
        print(f"❌ Erreur lecture CSV: {e}")
        return
    
    # Calculer les statistiques
    stats = {'Succès': 0, 'Warning': 0, 'Erreur': 0, 'Erreur!': 0, 'N/A': 0}
    for retailer in retailers_data:
        stats[retailer['global_status']] += 1
    
    # Générer HTML
    current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport SpiderVision Live - {current_time}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .dashboard-header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .logo-section {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .logo {{
            width: 40px;
            height: 40px;
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            color: white;
        }}
        .breadcrumb {{
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }}
        .breadcrumb .current {{
            color: white;
            font-weight: 500;
        }}
        .dashboard-controls {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            margin-bottom: 20px;
            border-radius: 12px;
            margin: 0 30px 20px 30px;
        }}
        .controls-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .control-btn {{
            padding: 8px 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }}
        .control-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }}
        .control-btn.primary {{
            background: rgba(59, 130, 246, 0.8);
            border-color: rgba(59, 130, 246, 0.8);
        }}
        .control-btn.primary:hover {{
            background: rgba(37, 99, 235, 0.9);
        }}
        tr.success td:not(:first-child) {{
            background-color: rgba(40, 167, 69, 0.2);
        }}
        tr.warning td:not(:first-child) {{
            background-color: rgba(255, 193, 7, 0.2);
        }}
        tr.error td:not(:first-child) {{
            background-color: rgba(220, 53, 69, 0.2);
        }}
        tr.error_critical td:not(:first-child) {{
            background-color: rgba(139, 0, 0, 0.3);
        }}
        td:first-child {{
            border-left: 2px solid #000;
            border-right: 2px solid #000;
            background-color: white !important;
        }}
        tr:first-child td:first-child {{
            border-top: 2px solid #000;
        }}
        tr:last-child td:first-child {{
            border-bottom: 2px solid #000;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
            margin: -30px -30px 30px -30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .filters {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .filter-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .filter-btn:hover, .filter-btn.active {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .btn-all {{ background: #6c757d; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: #212529; }}
        .btn-error {{ background: #dc3545; color: white; }}
        .btn-error-critical {{ background: #8b0000; color: white; }}
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
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        tr:hover {{
            background: #f8f9fa;
            transform: scale(1.01);
            transition: all 0.3s ease;
        }}
        .status {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status.success {{ background: #d4edda; color: #155724; }}
        .status.warning {{ background: #fff3cd; color: #856404; }}
        .status.error {{ background: #f8d7da; color: #721c24; }}
        .status.error-critical {{ background: #8b0000; color: white; }}
        .status.na {{ background: #e2e3e5; color: #383d41; }}
        .progress-bar {{
            width: 100%;
            height: 25px;
            background: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
            margin: 5px 0;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 12px;
            transition: width 1.2s ease-in-out;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 13px;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.4);
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
        .stacked-bars {{
            width: 100%;
        }}
        .progress-bar-small {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            margin: 3px 0;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }}
        .progress-fill.progress-blue {{
            background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
            color: white;
        }}
        .progress-fill.success-green {{
            background: linear-gradient(90deg, #28a745 0%, #1e7e34 100%);
            color: white;
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
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <div class="logo-section">
            <div class="logo">S</div>
            <div class="breadcrumb">
                Dashboard > <span class="current">SpiderVision Report</span>
            </div>
        </div>
    </div>
    
    <div class="dashboard-controls">
        <div class="controls-row">
            <button class="control-btn primary" onclick="filterTable('all')">Affichage Complet ({total_count})</button>
            <button class="control-btn" onclick="filterTable('success')">Succès Seulement ({stats['Succès']})</button>
            <button class="control-btn" onclick="filterTable('warning')">Warnings ({stats['Warning']})</button>
            <button class="control-btn" onclick="filterTable('error')">Erreurs ({stats['Erreur']})</button>
            <button class="control-btn" onclick="filterTable('error-critical')">Erreurs Critiques ({stats['Erreur!']})</button>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>📊 Rapport SpiderVision Live</h1>
            <p>Généré le {current_time}</p>
            <p>Données de {len(retailers_data)} enseignes</p>
        </div>
        
        <div class="table-container">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Enseigne</th>
                        <th>
                            Progress & Success (%)
                            <span class="info-icon" title="Bleu: Pourcentage du crawler qui a réussi | Vert: Pourcentage des magasins crawlés parfaitement">ℹ️</span>
                        </th>
                        <th>
                            Statut Progress
                            <span class="info-icon" title="Succès: ≥30% | Warning: 25-30% | Erreur: <25%">ℹ️</span>
                        </th>
                        <th>
                            Statut Success
                            <span class="info-icon" title="Succès: ≥95% | Warning: 90-95% | Erreur: <90%">ℹ️</span>
                        </th>
                    </tr>
                </thead>
                <tbody>"""
    
    # Ajouter les lignes de données
    for retailer in retailers_data:
        global_class = get_status_class(retailer['global_status']).replace('-', '_')
        html_content += f"""
                    <tr class="{global_class}" data-status="{retailer['global_status']}">
                        <td><strong>{retailer['name']}</strong></td>
                        <td>{create_stacked_progress_bars(retailer['progress'], retailer['progress_status'], retailer['success'], retailer['success_status'])}</td>
                        <td><span class="status {get_status_class(retailer['progress_status'])}">{retailer['progress_status']}</span></td>
                        <td><span class="status {get_status_class(retailer['success_status'])}">{retailer['success_status']}</span></td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        function filterTable(filter) {
            const rows = document.querySelectorAll('#dataTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            rows.forEach(row => {
                const status = row.dataset.status;
                let show = false;
                
                switch(filter) {
                    case 'all': show = true; break;
                    case 'success': show = status === 'Succès'; break;
                    case 'warning': show = status === 'Warning'; break;
                    case 'error': show = status === 'Erreur'; break;
                    case 'error-critical': show = status === 'Erreur!'; break;
                }
                
                row.style.display = show ? '' : 'none';
            });
        }
        
        // Animation des jauges
        document.addEventListener('DOMContentLoaded', function() {
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach((bar, index) => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, index * 50 + 500);
            });
        });
    </script>
</body>
</html>"""
    
    # Sauvegarder le fichier
    output_file = f'reports/last_day_history_live_report_{timestamp}.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Rapport généré: {output_file}")
    print(f"📊 Statistiques: Succès={stats['Succès']}, Warning={stats['Warning']}, Erreur={stats['Erreur']}, Erreur!={stats['Erreur!']}")
    
    return output_file

if __name__ == "__main__":
    generate_report_now()
