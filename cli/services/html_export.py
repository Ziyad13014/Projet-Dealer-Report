#!/usr/bin/env python3
"""Module pour l'export HTML des données SpiderVision."""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)

class HTMLExporter:
    """Générateur de rapports HTML pour les données SpiderVision."""
    
    def __init__(self):
        """Initialiser l'exporteur HTML"""
        pass
    
    def _parse_day_data(self, day_str: str) -> Dict[str, Any]:
        """Parser les données JSON d'un jour depuis une chaîne"""
        if not day_str or day_str == '':
            return {}
        try:
            # Remplacer les apostrophes par des guillemets pour un JSON valide
            day_str = day_str.replace("'", '"')
            return json.loads(day_str)
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def _get_status_class(self, crawling_rate: float, content_rate: float) -> str:
        """Déterminer la classe CSS basée sur les règles métier"""
        # Règle 1: % de magasins crawlés (>95% succès, 90-95% warning, <90% erreur)
        crawling_status = "success" if crawling_rate > 95 else "warning" if crawling_rate >= 90 else "error"
        
        # Règle 2: Taux de réussite avec contenu (>85% succès, 80-85% warning, <80% erreur)  
        content_status = "success" if content_rate > 85 else "warning" if content_rate >= 80 else "error"
        
        # Le statut final est le plus restrictif des deux
        if crawling_status == "error" or content_status == "error":
            return "status-error"
        elif crawling_status == "warning" or content_status == "warning":
            return "status-warning"
        else:
            return "status-success"
    
    def _get_rule_status(self, value: float, success_threshold: float, warning_threshold: float) -> str:
        """Déterminer le statut selon les seuils de règles"""
        if value > success_threshold:
            return "success"
        elif value >= warning_threshold:
            return "warning"
        else:
            return "error"
    
    def _format_progress_bar(self, value: float, max_value: float = 100) -> str:
        """Générer une barre de progression HTML"""
        percentage = min((value / max_value) * 100, 100) if max_value > 0 else 0
        status_class = "success" if percentage >= 90 else "warning" if percentage >= 70 else "danger"
        
        return f"""
        <div class="progress-container">
            <div class="progress-bar progress-bar-{status_class}" style="width: {percentage}%"></div>
            <span class="progress-text">{percentage:.1f}%</span>
        </div>
        """
    
    def _generate_history_chart(self, days_data: List[Dict[str, Any]]) -> str:
        """Générer un mini graphique pour l'historique des 6 derniers jours"""
        chart_bars = []
        for i, day_data in enumerate(days_data):
            success_percent = day_data.get('successPercent', 0)
            height = max(success_percent, 5)  # Minimum 5% pour la visibilité
            color_class = "success" if success_percent >= 90 else "warning" if success_percent >= 70 else "danger"
            
            chart_bars.append(f"""
                <div class="history-bar history-bar-{color_class}" 
                     style="height: {height}%" 
                     title="Jour {i}: {success_percent}%">
                </div>
            """)
        
        return f'<div class="history-chart">{"".join(chart_bars)}</div>'
    
    def generate_html_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """
        Générer un rapport HTML à partir des données overview.
        
        Args:
            data: Données JSON de l'API overview
            output_path: Chemin de sortie (optionnel)
            
        Returns:
            str: Chemin du fichier HTML généré
        """
        try:
            # Convertir les données en DataFrame pour faciliter le traitement
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                # Essayer de convertir directement
                df = pd.DataFrame([data] if isinstance(data, dict) else data)
            
            # Générer le nom de fichier si non fourni
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"reports/spider_vision_report_{timestamp}.html"
            
            # S'assurer que le répertoire existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Générer le contenu HTML
            html_content = self._generate_html_content(df)
            
            # Écrire le fichier
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Rapport HTML généré: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération HTML: {e}")
            raise
    
    def _generate_html_content(self, df: pd.DataFrame) -> str:
        """Générer le contenu HTML complet"""
        
        # Calculer les statistiques globales
        total_stores = df['storeCount'].fillna(0).sum()
        total_crawled = df['storeInDeltaCount'].fillna(0).sum()
        total_failed = df['storeFailedCount'].fillna(0).sum()
        total_success = df['successCount'].fillna(0).sum()
        
        overall_progress = (total_crawled / total_stores * 100) if total_stores > 0 else 0
        overall_success_rate = (total_success / total_crawled * 100) if total_crawled > 0 else 0
        
        # Générer les lignes du tableau
        table_rows = []
        for _, row in df.iterrows():
            if pd.isna(row['domainDealerName']) or row['domainDealerName'] == '':
                continue
                
            # Parser les données des 6 derniers jours
            days_data = []
            for i in range(6):
                day_key = f'day{i}'
                day_data = self._parse_day_data(str(row.get(day_key, '')))
                days_data.append(day_data)
            
            # Calculer les métriques depuis les données CSV
            stores_total = row.get('storeCount', 0) or 0
            stores_crawled = row.get('storeInDeltaCount', 0) or 0
            stores_failed = row.get('storeFailedCount', 0) or 0
            success_count = row.get('successCount', 0) or 0
            
            # Utiliser les valeurs de crawlProgress et crawlSuccessProgress directement depuis les données
            crawling_rate = float(row.get('crawlProgress', 0) or 0)
            content_rate = float(row.get('crawlSuccessProgress', 0) or 0)
            
            # Si les valeurs sont manquantes, calculer manuellement
            if crawling_rate == 0 and stores_total > 0:
                crawling_rate = (stores_crawled / stores_total * 100)
            
            if content_rate == 0 and stores_crawled > 0:
                content_rate = (success_count / stores_crawled * 100)
            
            # Déterminer le statut selon les règles métier
            status_class = self._get_status_class(crawling_rate, content_rate)
            
            # Statuts individuels pour affichage
            crawling_status = self._get_rule_status(crawling_rate, 95, 90)
            content_status = self._get_rule_status(content_rate, 85, 80)
            
            # Générer l'historique
            history_chart = self._generate_history_chart(days_data)
            
            # Déterminer le statut final pour le tri et le filtrage
            final_status = 'error' if crawling_status == 'error' or content_status == 'error' else 'warning' if crawling_status == 'warning' or content_status == 'warning' else 'success'
            
            table_rows.append({
                'html': f"""
                <tr class="{status_class} row-{final_status}" data-status="{final_status}" data-sort-order="{1 if final_status == 'success' else 2 if final_status == 'warning' else 3}">
                    <td class="dealer-info">
                        <div class="dealer-name">{row['domainDealerName']}</div>
                        <div class="dealer-id">ID: {row['domainDealerId']}</div>
                    </td>
                    <td class="text-center">{stores_total}</td>
                    <td class="text-center">{stores_crawled}</td>
                    <td class="text-center">{stores_failed}</td>
                    <td class="text-center">{success_count}</td>
                    <td>
                        <div class="rule-container">
                            <div class="rule-bar rule-{crawling_status}">
                                <span class="rule-text">{crawling_rate:.1f}%</span>
                            </div>
                            <div class="rule-label">Crawling (>95% ✓, 90-95% ⚠, <90% ✗)</div>
                        </div>
                    </td>
                    <td>
                        <div class="rule-container">
                            <div class="rule-bar rule-{content_status}">
                                <span class="rule-text">{content_rate:.1f}%</span>
                            </div>
                            <div class="rule-label">Contenu (>85% ✓, 80-85% ⚠, <80% ✗)</div>
                        </div>
                    </td>
                    <td class="status-cell">
                        <div class="status-badge status-badge-{final_status}">
                            {'✗ ERREUR' if final_status == 'error' else '⚠ WARNING' if final_status == 'warning' else '✓ SUCCÈS'}
                        </div>
                    </td>
                    <td>{history_chart}</td>
                </tr>
                """,
                'sort_order': 1 if final_status == 'success' else 2 if final_status == 'warning' else 3
            })
        
        # Template HTML complet
        html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport SpiderVision - {datetime.now().strftime('%d/%m/%Y %H:%M')}</title>
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
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
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
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #3498db;
        }}
        
        .stat-card.success {{ border-left-color: #27ae60; }}
        .stat-card.warning {{ border-left-color: #f39c12; }}
        .stat-card.danger {{ border-left-color: #e74c3c; }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
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
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 20px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.85em;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #ecf0f1;
            vertical-align: middle;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .dealer-info {{
            min-width: 150px;
        }}
        
        .dealer-name {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .dealer-id {{
            font-size: 0.8em;
            color: #7f8c8d;
        }}
        
        .progress-container {{
            position: relative;
            background: #ecf0f1;
            border-radius: 20px;
            height: 25px;
            min-width: 100px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            border-radius: 20px;
            transition: width 0.3s ease;
            position: relative;
        }}
        
        .progress-bar-success {{ background: linear-gradient(90deg, #27ae60, #2ecc71); }}
        .progress-bar-warning {{ background: linear-gradient(90deg, #f39c12, #e67e22); }}
        .progress-bar-danger {{ background: linear-gradient(90deg, #e74c3c, #c0392b); }}
        
        .progress-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 0.8em;
            font-weight: 600;
            color: #2c3e50;
            z-index: 2;
        }}
        
        .history-chart {{
            display: flex;
            align-items: end;
            gap: 2px;
            height: 30px;
            min-width: 80px;
        }}
        
        .history-bar {{
            flex: 1;
            min-height: 3px;
            border-radius: 2px 2px 0 0;
            transition: all 0.3s ease;
        }}
        
        .history-bar-success {{ background: #27ae60; }}
        .history-bar-warning {{ background: #f39c12; }}
        .history-bar-danger {{ background: #e74c3c; }}
        
        .history-bar:hover {{
            opacity: 0.7;
            transform: scaleY(1.1);
        }}
        
        .text-center {{ text-align: center; }}
        
        .status-success {{ background-color: rgba(39, 174, 96, 0.05); }}
        .status-warning {{ background-color: rgba(243, 156, 18, 0.05); }}
        .status-error {{ background-color: rgba(231, 76, 60, 0.05); }}
        
        .rule-container {{
            text-align: center;
            min-width: 120px;
        }}
        
        .rule-bar {{
            background: #ecf0f1;
            border-radius: 15px;
            height: 30px;
            position: relative;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }}
        
        .rule-success {{ background: linear-gradient(90deg, #27ae60, #2ecc71); color: white; }}
        .rule-warning {{ background: linear-gradient(90deg, #f39c12, #e67e22); color: white; }}
        .rule-error {{ background: linear-gradient(90deg, #e74c3c, #c0392b); color: white; }}
        
        .rule-label {{
            font-size: 0.7em;
            color: #7f8c8d;
            text-align: center;
            line-height: 1.2;
        }}
        
        .rule-text {{
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        .status-cell {{
            text-align: center;
            padding: 10px;
        }}
        
        .status-badge {{
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-badge-success {{
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            color: white;
        }}
        
        .status-badge-warning {{
            background: linear-gradient(90deg, #f39c12, #e67e22);
            color: white;
        }}
        
        .status-badge-error {{
            background: linear-gradient(90deg, #e74c3c, #c0392b);
            color: white;
        }}
        
        .filter-controls {{
            margin-top: 20px;
            text-align: center;
        }}
        
        .filter-controls h3 {{
            color: white;
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 400;
        }}
        
        .filter-buttons {{
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .filter-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }}
        
        .filter-success {{
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
        }}
        
        .filter-warning {{
            background: linear-gradient(135deg, #f39c12, #e67e22);
            color: white;
        }}
        
        .filter-error {{
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }}
        
        .filter-all {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
        }}
        
        .filter-btn:not(.active) {{
            opacity: 0.5;
            background: #95a5a6;
        }}
        
        .filter-icon {{
            font-size: 1.1em;
        }}
        
        .hidden-row {{
            display: none !important;
        }}
        
        .footer {{
            background: #34495e;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{ margin: 10px; }}
            .header h1 {{ font-size: 2em; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
            .table-container {{ padding: 15px; }}
            th, td {{ padding: 10px 8px; font-size: 0.9em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ SpiderVision Dashboard</h1>
            <div class="subtitle">Rapport de crawling - {datetime.now().strftime('%d/%m/%Y à %H:%M')}</div>
            
            <div class="filter-controls">
                <h3>Filtrer par statut :</h3>
                <div class="filter-buttons">
                    <button class="filter-btn filter-success active" data-status="success">
                        <span class="filter-icon">✓</span> Succès
                    </button>
                    <button class="filter-btn filter-warning active" data-status="warning">
                        <span class="filter-icon">⚠</span> Warning
                    </button>
                    <button class="filter-btn filter-error active" data-status="error">
                        <span class="filter-icon">✗</span> Erreur
                    </button>
                    <button class="filter-btn filter-all" onclick="toggleAllFilters()">
                        <span class="filter-icon">🔄</span> Tout afficher
                    </button>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{int(total_stores)}</div>
                <div class="stat-label">Magasins Total</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value">{int(total_crawled)}</div>
                <div class="stat-label">Magasins Crawlés</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-value">{int(total_failed)}</div>
                <div class="stat-label">Échecs</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value">{overall_progress:.1f}%</div>
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
                    {"".join([row['html'] for row in sorted(table_rows, key=lambda x: x['sort_order'])])}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Généré automatiquement par SpiderVision API • {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // Variables globales pour les filtres
        let activeFilters = new Set(['success', 'warning', 'error']);
        
        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            initializeFilters();
            addHistoryInteractions();
        });
        
        // Initialiser les filtres
        function initializeFilters() {
            document.querySelectorAll('.filter-btn[data-status]').forEach(btn => {
                btn.addEventListener('click', function() {
                    toggleFilter(this.dataset.status);
                });
            });
        }
        
        // Basculer un filtre
        function toggleFilter(status) {
            const btn = document.querySelector(`[data-status="${status}"]`);
            
            if (activeFilters.has(status)) {
                activeFilters.delete(status);
                btn.classList.remove('active');
            } else {
                activeFilters.add(status);
                btn.classList.add('active');
            }
            
            applyFilters();
            updateStats();
        }
        
        // Basculer tous les filtres
        function toggleAllFilters() {
            const allActive = activeFilters.size === 3;
            
            if (allActive) {
                // Tout désactiver
                activeFilters.clear();
                document.querySelectorAll('.filter-btn[data-status]').forEach(btn => {
                    btn.classList.remove('active');
                });
            } else {
                // Tout activer
                activeFilters = new Set(['success', 'warning', 'error']);
                document.querySelectorAll('.filter-btn[data-status]').forEach(btn => {
                    btn.classList.add('active');
                });
            }
            
            applyFilters();
            updateStats();
        }
        
        // Appliquer les filtres
        function applyFilters() {
            const rows = document.querySelectorAll('#retailer-table-body tr');
            
            rows.forEach(row => {
                const status = row.dataset.status;
                if (activeFilters.has(status)) {
                    row.classList.remove('hidden-row');
                } else {
                    row.classList.add('hidden-row');
                }
            });
        }
        
        // Mettre à jour les statistiques
        function updateStats() {
            const visibleRows = document.querySelectorAll('#retailer-table-body tr:not(.hidden-row)');
            let totalStores = 0, totalCrawled = 0, totalFailed = 0;
            
            visibleRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 4) {
                    totalStores += parseInt(cells[1].textContent) || 0;
                    totalCrawled += parseInt(cells[2].textContent) || 0;
                    totalFailed += parseInt(cells[3].textContent) || 0;
                }
            });
            
            // Mettre à jour les cartes de statistiques
            const statCards = document.querySelectorAll('.stat-value');
            if (statCards.length >= 3) {
                statCards[0].textContent = totalStores;
                statCards[1].textContent = totalCrawled;
                statCards[2].textContent = totalFailed;
                
                const overallProgress = totalStores > 0 ? (totalCrawled / totalStores * 100).toFixed(1) : 0;
                if (statCards[3]) statCards[3].textContent = overallProgress + '%';
            }
        }
        
        // Ajouter des interactions pour l'historique
        function addHistoryInteractions() {
            document.querySelectorAll('.history-bar').forEach(bar => {
                bar.addEventListener('mouseenter', function() {
                    this.style.transform = 'scaleY(1.2)';
                });
                bar.addEventListener('mouseleave', function() {
                    this.style.transform = 'scaleY(1)';
                });
            });
        }
        
        // Animation au chargement
        setTimeout(() => {
            document.querySelectorAll('.progress-bar').forEach(bar => {
                bar.style.width = bar.style.width;
            });
        }, 100);
    </script>
</body>
</html>
        """
        
{{ ... }}
