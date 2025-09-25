#!/usr/bin/env python3
"""
Génération d'un rapport HTML avec la correction du total stores
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_corrected_html_report():
    """Génère un rapport HTML avec les données corrigées"""
    
    # Lire le CSV existant
    csv_path = "reports/spider_vision_overview_current.csv"
    
    if not os.path.exists(csv_path):
        print(f" Fichier CSV non trouvé: {csv_path}")
        return
    
    print(f" Lecture du CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f" {len(df)} lignes trouvées")
    
    # Calculer les statistiques avec la logique corrigée (2 règles)
    success_count = 0
    warning_count = 0
    error_count = 0
    
    retailers_data = []
    
    for _, row in df.iterrows():
        # Extraire les données selon le vrai mapping SpiderVision
        name = row.get('domainDealerName', 'N/A')
        
        # crawlProgress = Global Progress (progression globale du crawl)
        global_progress = row.get('crawlProgress', 0)
        if pd.isna(global_progress) or global_progress == '':
            global_progress = 0
        else:
            global_progress = float(global_progress)
        
        # crawlSuccessProgress = Success (pourcentage de succès)
        success_rate = row.get('crawlSuccessProgress', 0)
        if pd.isna(success_rate) or success_rate == '':
            success_rate = 0
        else:
            success_rate = float(success_rate)
        
        # Appliquer les 2 règles métier:
        # Règle 1: Taux de succès (crawlSuccessProgress)
        success_status = 'erreur'
        if success_rate >= 95:
            success_status = 'succès'
        elif success_rate >= 90:
            success_status = 'avertissement'
        
        # Règle 2: Progression globale (crawlProgress) 
        progress_status = 'erreur'
        if global_progress >= 85:
            progress_status = 'succès'
        elif global_progress >= 80:
            progress_status = 'avertissement'
        
        # Statut final = le plus restrictif des deux
        if success_status == 'erreur' or progress_status == 'erreur':
            status = 'error'
            error_count += 1
        elif success_status == 'avertissement' or progress_status == 'avertissement':
            status = 'warning'
            warning_count += 1
        else:
            status = 'success'
            success_count += 1
        
        retailers_data.append({
            'name': name,
            'global_progress': global_progress,
            'success_rate': success_rate,
            'success_status': success_status,
            'progress_status': progress_status,
            'status': status
        })
    
    # Générer le HTML
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport SpiderVision Corrigé - {datetime.now().strftime('%d/%m/%Y %H:%M')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 300; }}
        .header .subtitle {{ font-size: 1.2em; opacity: 0.9; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
        .stat-card.success {{ border-left: 4px solid #27ae60; }}
        .stat-card.warning {{ border-left: 4px solid #f39c12; }}
        .stat-card.danger {{ border-left: 4px solid #e74c3c; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }}
        .stat-label {{ color: #7f8c8d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
        .table-container {{ padding: 30px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
        th {{ background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px 15px; text-align: left; font-weight: 600; }}
        th:first-child {{ width: 40%; }}
        th:nth-child(2), th:nth-child(3) {{ width: 20%; text-align: center; }}
        th:last-child {{ width: 20%; text-align: center; }}
        td {{ padding: 15px; border-bottom: 1px solid #ecf0f1; vertical-align: middle; }}
        td:first-child {{ font-weight: 600; color: #2c3e50; font-size: 1.1em; background: white !important; border-left: 2px solid #2c3e50; border-right: 2px solid #2c3e50; border-top: 1px solid #2c3e50; border-bottom: 1px solid #2c3e50; }}
        .percentage-cell {{ text-align: center; font-size: 1.4em; font-weight: bold; padding: 20px 10px; }}
        .final-status {{ text-align: center; font-size: 1.2em; font-weight: bold; padding: 20px 10px; }}
        .row-success {{ background: linear-gradient(135deg, rgba(39, 174, 96, 0.15), rgba(46, 204, 113, 0.15)); }}
        .row-success .percentage-cell {{ color: #27ae60; }}
        .row-success .final-status {{ background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; }}
        .row-warning {{ background: linear-gradient(135deg, rgba(243, 156, 18, 0.15), rgba(230, 126, 34, 0.15)); }}
        .row-warning .percentage-cell {{ color: #f39c12; }}
        .row-warning .final-status {{ background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }}
        .row-error {{ background: linear-gradient(135deg, rgba(231, 76, 60, 0.15), rgba(192, 57, 43, 0.15)); }}
        .row-error .percentage-cell {{ color: #e74c3c; }}
        .row-error .final-status {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; }}
        tr:hover {{ background-color: rgba(52, 152, 219, 0.05); }}
        .correction-note {{ background: #e8f5e8; border: 1px solid #27ae60; border-radius: 10px; padding: 20px; margin: 20px; }}
        .correction-note h3 {{ color: #27ae60; margin-bottom: 10px; }}
        .filter-controls {{ margin-top: 20px; text-align: center; }}
        .filter-controls h3 {{ color: white; margin-bottom: 15px; font-size: 1.1em; font-weight: 400; }}
        .filter-buttons {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 10px 20px; border: none; border-radius: 25px; font-size: 0.9em; font-weight: 600; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .filter-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.15); }}
        .filter-success {{ background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; }}
        .filter-warning {{ background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }}
        .filter-error {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; }}
        .filter-all {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; }}
        .filter-btn:not(.active) {{ opacity: 0.5; background: #95a5a6; }}
        .filter-icon {{ font-size: 1.1em; }}
        .hidden-row {{ display: none !important; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Tableau de Bord SpiderVision Corrigé</h1>
            <div class="subtitle">Rapport avec correction du total magasins - {datetime.now().strftime('%d/%m/%Y à %H:%M')} - {len(retailers_data)} enseignes</div>
            <div class="filter-controls">
                <h3>Filtrer par statut :</h3>
                <div class="filter-buttons">
                    <button class="filter-btn filter-success active" data-status="success">
                        <span class="filter-icon">✓</span> Succès ({success_count})
                    </button>
                    <button class="filter-btn filter-warning active" data-status="warning">
                        <span class="filter-icon">⚠</span> Avertissements ({warning_count})
                    </button>
                    <button class="filter-btn filter-error active" data-status="error">
                        <span class="filter-icon">✗</span> Erreurs ({error_count})
                    </button>
                    <button class="filter-btn filter-all" onclick="toggleAllFilters()">
                        <span class="filter-icon">🔄</span> Tout Afficher/Masquer
                    </button>
                </div>
            </div>
        </div>
        
        
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Enseigne</th>
                        <th>Progression Globale (%)</th>
                        <th>Taux de Succès (%)</th>
                        <th>Statut Final</th>
                    </tr>
                </thead>
                <tbody>"""
    
    # Ajouter les lignes du tableau
    for retailer in retailers_data:
        status_class = f"status-{retailer['status']}"
        badge_class = f"status-badge-{retailer['status']}"
        status_text = {
            'success': 'Succès',
            'warning': 'Avertissement', 
            'error': 'Erreur'
        }[retailer['status']]
        
        # Classe pour toute la ligne selon le statut final
        row_class = {
            'success': 'row-success',
            'warning': 'row-warning',
            'error': 'row-error'
        }[retailer['status']]
        
        html_content += f"""
                    <tr class="{row_class}" data-status="{retailer['status']}">
                        <td>{retailer['name']}</td>
                        <td class="percentage-cell">{retailer['global_progress']:.1f}%</td>
                        <td class="percentage-cell">{retailer['success_rate']:.1f}%</td>
                        <td class="final-status">{status_text}</td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>📊 Rapport généré avec les corrections et les 2 règles métier - Tableau de Bord SpiderVision</p>
        </div>
    </div>
    
    <script>
        // Gestion des filtres
        document.addEventListener('DOMContentLoaded', function() {
            const filterButtons = document.querySelectorAll('.filter-btn[data-status]');
            const rows = document.querySelectorAll('tbody tr[data-status]');
            
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    this.classList.toggle('active');
                    updateVisibility();
                });
            });
            
            function updateVisibility() {
                const activeFilters = Array.from(filterButtons)
                    .filter(btn => btn.classList.contains('active'))
                    .map(btn => btn.dataset.status);
                
                rows.forEach(row => {
                    const status = row.dataset.status;
                    if (activeFilters.includes(status)) {
                        row.classList.remove('hidden-row');
                    } else {
                        row.classList.add('hidden-row');
                    }
                });
            }
        });
        
        function toggleAllFilters() {
            const filterButtons = document.querySelectorAll('.filter-btn[data-status]');
            const allActive = Array.from(filterButtons).every(btn => btn.classList.contains('active'));
            
            filterButtons.forEach(button => {
                if (allActive) {
                    button.classList.remove('active');
                } else {
                    button.classList.add('active');
                }
            });
            
            const rows = document.querySelectorAll('tbody tr[data-status]');
            rows.forEach(row => {
                if (allActive) {
                    row.classList.add('hidden-row');
                } else {
                    row.classList.remove('hidden-row');
                }
            });
        }
    </script>
</body>
</html>"""
    
    # Sauvegarder le fichier
    output_path = "reports/spider_vision_corrected_report.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Rapport corrigé avec filtres généré: {output_path}")
    print(f"📊 Statistiques avec les 2 règles métier et filtres interactifs:")
    print(f"   - Succès: {success_count}")
    print(f"   - Avertissements: {warning_count}")
    print(f"   - Erreurs: {error_count}")
    print(f"   - Total enseignes: {len(retailers_data)}")

if __name__ == "__main__":
    generate_corrected_html_report()
