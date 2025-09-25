#!/usr/bin/env python3
"""Génération manuelle du rapport HTML avec toutes les enseignes depuis le CSV"""

import os
import pandas as pd
import json
from datetime import datetime

def parse_day_data(day_str):
    """Parse les données d'un jour depuis le CSV"""
    if not day_str or day_str == "" or pd.isna(day_str):
        return {"successPercent": 0, "progress": 0}
    
    try:
        day_str = str(day_str).replace("'", '"')
        data = json.loads(day_str)
        return {
            "successPercent": data.get("successPercent", 0),
            "progress": data.get("progress", 0)
        }
    except:
        return {"successPercent": 0, "progress": 0}

def determine_status(crawl_progress, crawl_success_progress):
    """Détermine le statut selon les règles métier"""
    crawl_progress = float(crawl_progress) if crawl_progress and not pd.isna(crawl_progress) else 0
    crawl_success_progress = float(crawl_success_progress) if crawl_success_progress and not pd.isna(crawl_success_progress) else 0
    
    # Règles de crawling
    if crawl_progress >= 95:
        crawl_status = "success"
    elif crawl_progress >= 90:
        crawl_status = "warning"
    else:
        crawl_status = "error"
    
    # Règles de contenu
    if crawl_success_progress >= 85:
        content_status = "success"
    elif crawl_success_progress >= 80:
        content_status = "warning"
    else:
        content_status = "error"
    
    # Statut final (le plus restrictif)
    if crawl_status == "error" or content_status == "error":
        return "error"
    elif crawl_status == "warning" or content_status == "warning":
        return "warning"
    else:
        return "success"

def main():
    try:
        print("🔄 Génération manuelle du rapport HTML complet...")
        
        # Lire le CSV
        csv_path = "reports/spider_vision_overview_current.csv"
        if not os.path.exists(csv_path):
            print(f"❌ Fichier CSV non trouvé: {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        print(f"📊 {len(df)} lignes trouvées dans le CSV")
        
        # Filtrer les lignes avec des données valides (nom d'enseigne non vide)
        df_valid = df[df['domainDealerName'].notna() & (df['domainDealerName'] != '')]
        print(f"✅ {len(df_valid)} enseignes avec données valides")
        
        # Calculer les statistiques et générer les lignes HTML
        html_rows = []
        status_counts = {"success": 0, "warning": 0, "error": 0}
        total_stores = 0
        total_crawled = 0
        total_failed = 0
        
        for _, row in df_valid.iterrows():
            crawl_progress = row['crawlProgress'] if not pd.isna(row['crawlProgress']) else 0
            crawl_success_progress = row['crawlSuccessProgress'] if not pd.isna(row['crawlSuccessProgress']) else 0
            store_count = int(row['storeCount']) if not pd.isna(row['storeCount']) else 0
            success_count = int(row['successCount']) if not pd.isna(row['successCount']) else 0
            failed_count = int(row['storeFailedCount']) if not pd.isna(row['storeFailedCount']) else 0
            
            total_stores += store_count
            total_crawled += success_count
            total_failed += failed_count
            
            status = determine_status(crawl_progress, crawl_success_progress)
            status_counts[status] += 1
            
            # Générer les barres d'historique
            history_data = []
            for day in ['day0', 'day1', 'day2', 'day3', 'day4', 'day5']:
                day_data = parse_day_data(row[day])
                history_data.append(day_data['successPercent'])
            
            history_bars = ""
            for i, percent in enumerate(history_data):
                if percent >= 95:
                    bar_class = "history-bar-success"
                elif percent >= 80:
                    bar_class = "history-bar-warning"
                else:
                    bar_class = "history-bar-danger"
                
                height = max(3, percent) if percent > 0 else 3
                history_bars += f'<div class="history-bar {bar_class}" style="height: {height}%" title="Jour {i}: {percent}%"></div>'
            
            # Classes CSS pour les règles
            crawl_rule_class = "rule-success" if crawl_progress >= 95 else ("rule-warning" if crawl_progress >= 90 else "rule-error")
            content_rule_class = "rule-success" if crawl_success_progress >= 85 else ("rule-warning" if crawl_success_progress >= 80 else "rule-error")
            
            # Badge de statut
            status_badges = {
                "success": "✓ SUCCÈS",
                "warning": "⚠ WARNING", 
                "error": "✗ ERREUR"
            }
            
            sort_order = {"success": 1, "warning": 2, "error": 3}[status]
            
            html_row = f'''
    <tr class="status-{status} row-{status}" data-status="{status}" data-sort-order="{sort_order}">
        <td class="dealer-info">
            <div class="dealer-name">{row['domainDealerName']}</div>
            <div class="dealer-id">ID: {row['domainDealerId']}</div>
        </td>
        <td class="text-center">{store_count}</td>
        <td class="text-center">{success_count}</td>
        <td class="text-center">{failed_count}</td>
        <td class="text-center">{success_count}</td>
        <td>
            <div class="rule-container">
                <div class="rule-bar {crawl_rule_class}">
                    <span class="rule-text">{crawl_progress:.1f}%</span>
                </div>
                <div class="rule-label">Crawling (>95% ✓, 90-95% ⚠, <90% ✗)</div>
            </div>
        </td>
        <td>
            <div class="rule-container">
                <div class="rule-bar {content_rule_class}">
                    <span class="rule-text">{crawl_success_progress:.1f}%</span>
                </div>
                <div class="rule-label">Contenu (>85% ✓, 80-85% ⚠, <80% ✗)</div>
            </div>
        </td>
        <td class="status-cell">
            <div class="status-badge status-badge-{status}">
                {status_badges[status]}
            </div>
        </td>
        <td>
            <div class="history-chart">
                {history_bars}
            </div>
        </td>
    </tr>'''
            
            html_rows.append((sort_order, html_row))
        
        # Trier les lignes par statut (succès d'abord)
        html_rows.sort(key=lambda x: x[0])
        sorted_html_rows = [row[1] for row in html_rows]
        
        overall_progress = (total_crawled / total_stores * 100) if total_stores > 0 else 0
        
        print(f"📊 Statistiques calculées:")
        print(f"   • Succès: {status_counts['success']}")
        print(f"   • Warning: {status_counts['warning']}")
        print(f"   • Erreur: {status_counts['error']}")
        print(f"   • Total magasins: {total_stores}")
        print(f"   • Progrès global: {overall_progress:.1f}%")
        
        # Générer le fichier HTML complet
        output_path = "reports/spider_vision_complete_report.html"
        
        # Écraser le fichier existant avec le contenu complet
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport SpiderVision Complet - {datetime.now().strftime("%d/%m/%Y %H:%M")}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 300; }}
        .header .subtitle {{ font-size: 1.2em; opacity: 0.9; }}
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
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-left: 4px solid #3498db; }}
        .stat-card.success {{ border-left-color: #27ae60; }}
        .stat-card.warning {{ border-left-color: #f39c12; }}
        .stat-card.danger {{ border-left-color: #e74c3c; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }}
        .stat-label {{ color: #7f8c8d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
        .table-container {{ padding: 30px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
        th {{ background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 20px 15px; text-align: left; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.85em; }}
        td {{ padding: 15px; border-bottom: 1px solid #ecf0f1; vertical-align: middle; }}
        tr:hover {{ background-color: #f8f9fa; }}
        .dealer-info {{ min-width: 150px; }}
        .dealer-name {{ font-weight: 600; color: #2c3e50; margin-bottom: 5px; }}
        .dealer-id {{ font-size: 0.8em; color: #7f8c8d; }}
        .rule-container {{ text-align: center; min-width: 120px; }}
        .rule-bar {{ background: #ecf0f1; border-radius: 15px; height: 30px; position: relative; margin-bottom: 5px; display: flex; align-items: center; justify-content: center; font-weight: 600; }}
        .rule-success {{ background: linear-gradient(90deg, #27ae60, #2ecc71); color: white; }}
        .rule-warning {{ background: linear-gradient(90deg, #f39c12, #e67e22); color: white; }}
        .rule-error {{ background: linear-gradient(90deg, #e74c3c, #c0392b); color: white; }}
        .rule-label {{ font-size: 0.7em; color: #7f8c8d; text-align: center; line-height: 1.2; }}
        .rule-text {{ font-size: 0.9em; font-weight: 600; }}
        .status-cell {{ text-align: center; padding: 10px; }}
        .status-badge {{ padding: 8px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
        .status-badge-success {{ background: linear-gradient(90deg, #27ae60, #2ecc71); color: white; }}
        .status-badge-warning {{ background: linear-gradient(90deg, #f39c12, #e67e22); color: white; }}
        .status-badge-error {{ background: linear-gradient(90deg, #e74c3c, #c0392b); color: white; }}
        .history-chart {{ display: flex; align-items: end; gap: 2px; height: 30px; min-width: 80px; }}
        .history-bar {{ flex: 1; min-height: 3px; border-radius: 2px 2px 0 0; transition: all 0.3s ease; }}
        .history-bar-success {{ background: #27ae60; }}
        .history-bar-warning {{ background: #f39c12; }}
        .history-bar-danger {{ background: #e74c3c; }}
        .history-bar:hover {{ opacity: 0.7; transform: scaleY(1.1); }}
        .text-center {{ text-align: center; }}
        .status-success {{ background-color: rgba(39, 174, 96, 0.05); }}
        .status-warning {{ background-color: rgba(243, 156, 18, 0.05); }}
        .status-error {{ background-color: rgba(231, 76, 60, 0.05); }}
        .hidden-row {{ display: none !important; }}
        .footer {{ background: #34495e; color: white; text-align: center; padding: 20px; font-size: 0.9em; }}
        @media (max-width: 768px) {{ .container {{ margin: 10px; }} .header h1 {{ font-size: 2em; }} .stats-grid {{ grid-template-columns: 1fr 1fr; }} .table-container {{ padding: 15px; }} th, td {{ padding: 10px 8px; font-size: 0.9em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ SpiderVision Dashboard Complet</h1>
            <div class="subtitle">Rapport de crawling - {datetime.now().strftime("%d/%m/%Y à %H:%M")} - {len(df_valid)} enseignes</div>
            <div class="filter-controls">
                <h3>Filtrer par statut :</h3>
                <div class="filter-buttons">
                    <button class="filter-btn filter-success active" data-status="success">
                        <span class="filter-icon">✓</span> Succès ({status_counts['success']})
                    </button>
                    <button class="filter-btn filter-warning active" data-status="warning">
                        <span class="filter-icon">⚠</span> Warning ({status_counts['warning']})
                    </button>
                    <button class="filter-btn filter-error active" data-status="error">
                        <span class="filter-icon">✗</span> Erreur ({status_counts['error']})
                    </button>
                    <button class="filter-btn filter-all" onclick="toggleAllFilters()">
                        <span class="filter-icon">🔄</span> Tout afficher
                    </button>
                </div>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-stores">{total_stores}</div>
                <div class="stat-label">Magasins Total</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value" id="total-crawled">{total_crawled}</div>
                <div class="stat-label">Magasins Crawlés</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-value" id="total-failed">{total_failed}</div>
                <div class="stat-label">Échecs</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value" id="overall-progress">{overall_progress:.1f}%</div>
                <div class="stat-label">Progrès Global</div>
            </div>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Retailer</th>
                        <th>Total</th>
                        <th>Crawlés</th>
                        <th>Échecs</th>
                        <th>Succès</th>
                        <th>Règle 1: Crawling</th>
                        <th>Règle 2: Contenu</th>
                        <th>Statut Final</th>
                        <th>Historique 6j</th>
                    </tr>
                </thead>
                <tbody id="retailer-table-body">
                    {''.join(sorted_html_rows)}
                </tbody>
            </table>
        </div>
        <div class="footer">
            <p>Généré automatiquement par SpiderVision API • {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")} • {len(df_valid)} enseignes</p>
        </div>
    </div>
    <script>
        let activeFilters = new Set(['success', 'warning', 'error']);
        document.addEventListener('DOMContentLoaded', function() {{
            initializeFilters();
            addHistoryInteractions();
        }});
        function initializeFilters() {{
            document.querySelectorAll('.filter-btn[data-status]').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    toggleFilter(this.dataset.status);
                }});
            }});
        }}
        function toggleFilter(status) {{
            const btn = document.querySelector(`[data-status="${{status}}"]`);
            if (activeFilters.has(status)) {{
                activeFilters.delete(status);
                btn.classList.remove('active');
            }} else {{
                activeFilters.add(status);
                btn.classList.add('active');
            }}
            applyFilters();
            updateStats();
        }}
        function toggleAllFilters() {{
            const allActive = activeFilters.size === 3;
            if (allActive) {{
                activeFilters.clear();
                document.querySelectorAll('.filter-btn[data-status]').forEach(btn => {{
                    btn.classList.remove('active');
                }});
            }} else {{
                activeFilters = new Set(['success', 'warning', 'error']);
                document.querySelectorAll('.filter-btn[data-status]').forEach(btn => {{
                    btn.classList.add('active');
                }});
            }}
            applyFilters();
            updateStats();
        }}
        function applyFilters() {{
            const rows = document.querySelectorAll('#retailer-table-body tr');
            rows.forEach(row => {{
                const status = row.dataset.status;
                if (activeFilters.has(status)) {{
                    row.classList.remove('hidden-row');
                }} else {{
                    row.classList.add('hidden-row');
                }}
            }});
        }}
        function updateStats() {{
            const visibleRows = document.querySelectorAll('#retailer-table-body tr:not(.hidden-row)');
            let totalStores = 0, totalCrawled = 0, totalFailed = 0;
            visibleRows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                if (cells.length >= 4) {{
                    totalStores += parseInt(cells[1].textContent) || 0;
                    totalCrawled += parseInt(cells[2].textContent) || 0;
                    totalFailed += parseInt(cells[3].textContent) || 0;
                }}
            }});
            document.getElementById('total-stores').textContent = totalStores;
            document.getElementById('total-crawled').textContent = totalCrawled;
            document.getElementById('total-failed').textContent = totalFailed;
            const overallProgress = totalStores > 0 ? (totalCrawled / totalStores * 100).toFixed(1) : 0;
            document.getElementById('overall-progress').textContent = overallProgress + '%';
        }}
        function addHistoryInteractions() {{
            document.querySelectorAll('.history-bar').forEach(bar => {{
                bar.addEventListener('mouseenter', function() {{
                    this.style.transform = 'scaleY(1.2)';
                }});
                bar.addEventListener('mouseleave', function() {{
                    this.style.transform = 'scaleY(1)';
                }});
            }});
        }}
    </script>
</body>
</html>''')
        
        print(f"✅ Rapport HTML complet généré: {output_path}")
        
        # Vérifier le fichier
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"📄 Taille du fichier: {size:,} bytes")
            
            abs_path = os.path.abspath(output_path).replace('\\', '/')
            print(f"🔗 Ouvrir: file:///{abs_path}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
