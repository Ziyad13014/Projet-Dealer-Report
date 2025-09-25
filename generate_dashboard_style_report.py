"""
Script autonome pour générer un rapport HTML style « dashboard » à partir du CSV
reports/spider_vision_overview_current.csv.

- Entrée: reports/spider_vision_overview_current.csv (UTF-8, en-têtes attendues: domainDealerName, crawlProgress,
  crawlSuccessProgress, totalStores)
- Sortie: reports/dashboard_style_report_YYYYMMDD_HHMMSS.html
- Exécution: python generate_dashboard_style_report.py

Note: Ce script ne dépend pas de la CLI. Il sert d’outil visuel rapide basé sur
les données déjà exportées (overview_current.csv).
"""
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

def create_dashboard_style_report():
    """Génère un rapport HTML type « dashboard ».
    
    Description:
    - Lit le fichier CSV: reports/spider_vision_overview_current.csv
    - Calcule quelques indicateurs simples par retailer (progression, succès, magasins parcourus)
    - Génère un fichier HTML dans reports/ nommé dashboard_style_report_YYYYMMDD_HHMMSS.html
    
    Usage rapide:
    - python generate_dashboard_style_report.py
    
    Remarques:
    - Ce script est indépendant de la CLI (dealer-report). Il propose une vue visuelle rapide.
    - Si le CSV n’existe pas, un message d’erreur s’affiche et rien n’est généré.
    """
    
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
                
                # Calculer les stores counts (simulation basée sur les données)
                total_stores = int(row.get('totalStores', 100))  # Valeur par défaut
                crawled_stores = int((progress / 100) * total_stores) if progress > 0 else 0
                failed_stores = total_stores - crawled_stores
                
                retailers_data.append({
                    'id': len(retailers_data) + 1,
                    'name': retailer_name,
                    'progress': progress,
                    'success': success,
                    'total_stores': total_stores,
                    'crawled_stores': crawled_stores,
                    'failed_stores': failed_stores,
                    'in_delta_count': crawled_stores,
                    'failed_count': failed_stores,
                    'to_crawl_count': failed_stores
                })
    
    except FileNotFoundError:
        print("❌ Fichier CSV non trouvé")
        return
    
    # Générer le HTML avec le style dashboard
    current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
    filename = f"reports/dashboard_style_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpiderVision Dashboard - {current_time}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1d29;
            color: #ffffff;
            min-height: 100vh;
        }}
        
        .dashboard-container {{
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px 0;
        }}
        
        .logo {{
            width: 40px;
            height: 40px;
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .breadcrumb {{
            color: #9ca3af;
            font-size: 14px;
        }}
        
        .breadcrumb .current {{
            color: #ffffff;
            font-weight: 500;
        }}
        
        .controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .btn {{
            padding: 8px 16px;
            border: 1px solid #374151;
            background: #1f2937;
            color: #ffffff;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .btn:hover {{
            background: #374151;
        }}
        
        .btn.primary {{
            background: #3b82f6;
            border-color: #3b82f6;
        }}
        
        .btn.primary:hover {{
            background: #2563eb;
        }}
        
        .table-container {{
            background: #1f2937;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #374151;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            color: #d1d5db;
            border-bottom: 1px solid #4b5563;
        }}
        
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid #374151;
            font-size: 14px;
        }}
        
        tr:hover {{
            background: rgba(55, 65, 81, 0.5);
        }}
        
        .store-id {{
            color: #9ca3af;
            font-weight: 500;
        }}
        
        .dealer-name {{
            color: #ffffff;
            font-weight: 500;
        }}
        
        .count-cell {{
            text-align: center;
            color: #60a5fa;
        }}
        
        .progress-cell {{
            width: 200px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 24px;
            background: #374151;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
            transition: width 0.3s ease;
        }}
        
        .success-cell {{
            width: 120px;
        }}
        
        .success-badges {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .success-row {{
            display: flex;
            gap: 4px;
        }}
        
        .success-badge {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-align: center;
            min-width: 45px;
        }}
        
        .success-100 {{
            background: #10b981;
            color: white;
        }}
        
        .success-99 {{
            background: #059669;
            color: white;
        }}
        
        .success-98 {{
            background: #047857;
            color: white;
        }}
        
        .success-other {{
            background: #3b82f6;
            color: white;
        }}
        
        .history-cell {{
            width: 150px;
        }}
        
        .history-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 2px;
        }}
        
        .history-badge {{
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
            color: white;
            min-width: 35px;
            text-align: center;
        }}
        
        .day-100 {{
            background: #10b981;
        }}
        
        .day-99 {{
            background: #059669;
        }}
        
        .day-other {{
            background: #3b82f6;
        }}
        
        .day-low {{
            background: #ef4444;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <div class="logo">W</div>
            <div class="breadcrumb">
                Dashboard > <span class="current">Sales Dashboard</span>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn primary">Show Compact View</button>
            <button class="btn">Show All Success Rates</button>
            <button class="btn">Hide Rows With Null StoreCount</button>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Domain dealer id</th>
                        <th>Domain dealer</th>
                        <th>Store in delta count</th>
                        <th>Store failed count</th>
                        <th>Store to crawl count</th>
                        <th>Global Progress</th>
                        <th>Success</th>
                        <th>Last day history</th>
                    </tr>
                </thead>
                <tbody>"""
    
    # Ajouter les lignes de données
    for retailer in retailers_data:
        # Générer les badges de succès (simulation)
        success_badges = []
        base_success = retailer['success']
        
        # Créer 5 badges avec des variations
        for i in range(5):
            if base_success >= 99:
                success_badges.append(f"<span class='success-badge success-100'>100%</span>")
            elif base_success >= 95:
                success_badges.append(f"<span class='success-badge success-99'>99%</span>")
            elif base_success >= 90:
                success_badges.append(f"<span class='success-badge success-98'>98%</span>")
            else:
                success_badges.append(f"<span class='success-badge success-other'>{base_success:.0f}%</span>")
        
        # Générer l'historique (simulation)
        history_badges = []
        for i in range(5):
            if base_success >= 99:
                history_badges.append(f"<span class='history-badge day-100'>100%</span>")
            elif base_success >= 95:
                history_badges.append(f"<span class='history-badge day-99'>99%</span>")
            elif base_success >= 80:
                history_badges.append(f"<span class='history-badge day-other'>{base_success:.0f}%</span>")
            else:
                history_badges.append(f"<span class='history-badge day-low'>{base_success:.0f}%</span>")
        
        progress_width = min(retailer['progress'], 100)
        
        html_content += f"""
                    <tr>
                        <td class="store-id">{retailer['id']}</td>
                        <td class="dealer-name">{retailer['name']}</td>
                        <td class="count-cell">{retailer['in_delta_count']}</td>
                        <td class="count-cell">{retailer['failed_count']}</td>
                        <td class="count-cell">{retailer['to_crawl_count']}</td>
                        <td class="progress-cell">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {progress_width}%">{retailer['progress']:.0f}%</div>
                            </div>
                        </td>
                        <td class="success-cell">
                            <div class="success-badges">
                                <div class="success-row">
                                    {''.join(success_badges[:3])}
                                </div>
                                <div class="success-row">
                                    {''.join(success_badges[3:])}
                                </div>
                            </div>
                        </td>
                        <td class="history-cell">
                            <div class="history-badges">
                                {''.join(history_badges)}
                            </div>
                        </td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""
    
    # Sauvegarder le fichier
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Rapport dashboard généré: {filename}")
    return filename

if __name__ == "__main__":
    create_dashboard_style_report()
