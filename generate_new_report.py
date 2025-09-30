import csv
import ast
import json
import base64
import os
from datetime import datetime
from dotenv import load_dotenv

def get_logo_base64():
    """Convertit le logo en base64 pour l'intégrer dans le HTML"""
    logo_path = 'logospdervision.png'
    try:
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded}"
        else:
            # Si le logo n'existe pas, retourner une image vide
            return ""
    except Exception as e:
        print(f"⚠️ Impossible de charger le logo: {e}")
        return ""

def get_gradient_color(value):
    """Retourne une couleur en dégradé selon le pourcentage.
    0% = Rouge foncé, 50% = Orange, 90% = Jaune, 95%+ = Vert"""
    if value >= 95:
        return "#10b981"  # Vert succès
    elif value >= 90:
        return "#fbbf24"  # Jaune (warning)
    elif value >= 70:
        return "#fb923c"  # Orange
    elif value >= 50:
        return "#f87171"  # Rouge clair
    elif value >= 25:
        return "#ef4444"  # Rouge
    else:
        return "#dc2626"  # Rouge foncé

def create_stacked_progress_bars(progress_val, progress_status, success_val, success_status):
    """Crée deux barres de progression empilées avec couleurs distinctes.
    Affiche uniquement le pourcentage sur les jauges (sans statut)."""
    progress_width = min(progress_val, 100)
    success_width = min(success_val, 100)
    
    # Couleur fixe pour Progress (bleu)
    progress_color = "progress-blue"
    
    # Couleur dynamique pour Success basée sur le pourcentage
    success_gradient_color = get_gradient_color(success_val)
    
    # Styles de largeur
    progress_style = f"width: {progress_width}%"
    success_style = f"width: {success_width}%; background: linear-gradient(90deg, {success_gradient_color} 0%, {success_gradient_color} 100%)"
    
    # Libellés: pourcentage uniquement
    progress_label = f"{progress_val:.1f}%"
    success_label = f"{success_val:.1f}%"
    
    if progress_val == 0:
        progress_bar_content = f"""<div class="progress-bar-small">
            <div class="progress-fill-zero">{progress_label}</div>
        </div>"""
    else:
        progress_bar_content = f"""<div class="progress-bar-small">
            <div class="progress-fill {progress_color}" style="{progress_style}">{progress_label}</div>
        </div>"""
    
    if success_val == 0:
        success_bar_content = f"""<div class="progress-bar-small">
            <div class="progress-fill-zero">{success_label}</div>
        </div>"""
    else:
        success_bar_content = f"""<div class="progress-bar-small">
            <div class="progress-fill" style="{success_style}; color: white;">{success_label}</div>
        </div>"""
    
    return f"""<div class="stacked-bars">
        {progress_bar_content}
        {success_bar_content}
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

def generate_new_report():
    """Génère un nouveau rapport avec la mise en page améliorée"""
    print("🔄 Génération nouveau rapport en cours...")
    

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
                
                # Compteurs additionnels (si présents)
                store_count = int(row.get('storeCount', 0) or 0)
                success_count = int(row.get('successCount', 0) or 0)
                failed_count = int(row.get('storeFailedCount', 0) or 0)
                in_delta_count = int(row.get('storeInDeltaCount', 0) or 0)
                to_crawl_count = int(row.get('storeToCrawl', 0) or 0)

                data = {
                    'name': retailer_name,
                    'progress': progress,
                    'success': success,
                    'progress_status': progress_status,
                    'success_status': success_status,
                    'global_status': global_status,
                    'store_count': store_count,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'in_delta_count': in_delta_count,
                    'to_crawl_count': to_crawl_count
                }
                # Historique: conserver day0..day5 bruts (si fournis) pour le JS
                for i in range(6):
                    key = f'day{i}'
                    if key in row:
                        data[key] = row.get(key, '')

                retailers_data.append(data)
    
    except FileNotFoundError:
        print("❌ Fichier CSV non trouvé")
        return
    
    # Calculer les statistiques
    stats = {
        'Succès': 0,
        'Warning': 0,
        'Erreur': 0,
        'Erreur!': 0,
        'N/A': 0
    }
    
    for retailer in retailers_data:
        status = retailer['global_status']
        if status in stats:
            stats[status] += 1
    
    total_count = len(retailers_data)
    
    # Trier les données pour prioriser les erreurs
    # Ordre de priorité: Erreur > Erreur! > Warning > Succès > N/A
    status_priority = {
        'Erreur': 0,
        'Erreur!': 1,
        'Warning': 2,
        'Succès': 3,
        'N/A': 4
    }
    retailers_data.sort(key=lambda x: status_priority.get(x['global_status'], 5))
    
    # Générer le HTML
    current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
    filename = f"reports/last_day_history_live_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Convertir le logo en base64 pour un fichier HTML autonome
    logo_base64 = get_logo_base64()
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport SpiderVision Live - {current_time}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter, sans-serif;
            background: #1a1d29;
            color: #ffffff;
            min-height: 100vh;
        }}
        .filters {{
            padding: 20px 30px;
            background: #2d3748;
            border-bottom: 1px solid #4a5568;
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
        .modal-body {{ padding: 16px 18px; line-height: 1.6; }}
        .kv {{ display: grid; grid-template-columns: 200px 1fr; gap: 8px 16px; margin-bottom: 12px; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 12px; }}
        .badge.success {{ background: rgba(40,167,69,.15); color: #4ade80; border: 1px solid rgba(74,222,128,.35); }}
        .badge.warning {{ background: rgba(255,193,7,.15); color: #fde047; border: 1px solid rgba(253,224,71,.35); }}
        .badge.error {{ background: rgba(220,53,69,.15); color: #fca5a5; border: 1px solid rgba(252,165,165,.35); }}
        .badge.error-critical {{ background: rgba(139,0,0,.25); color: #fecaca; border: 1px solid rgba(254,202,202,.35); }}
        .history {{ margin-top: 10px; }}
        .history h4 {{ margin-bottom: 6px; font-size: 14px; color: #9ca3af; }}
        .history ul {{ list-style: disc; margin-left: 20px; color: #e5e7eb; }}
        .detail-intro {{ background: #1f2937; padding: 10px; border-radius: 6px; margin-bottom: 12px; color: #e5e7eb; }}
        .detail-intro .intro-list {{ margin-top: 6px; margin-left: 18px; list-style: disc; }}
        .legend {{ margin: 8px 0 4px 0; color: #9ca3af; }}
        td:first-child {{
            border-left: 2px solid #000;
            border-right: 2px solid #000;
            background-color: #1f2937 !important;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        tr:first-child td:first-child {{
            border-top: 2px solid #000;
        }}
        tr:last-child td:first-child {{
            border-bottom: 2px solid #000;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #1f2937;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: #374151;
            color: white;
            padding: 8px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 8px;
            margin-bottom: 20px;
            height: 40px;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .logo {{
            width: 48px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .logo img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .header-time {{
            font-size: 0.9em;
            font-weight: 500;
        }}
        .table-container {{
            background: #1f2937;
            border-radius: 8px;
            overflow: hidden;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
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
        /* Column widths: make 'Enseigne' smaller, others larger */
        th:nth-child(1), td:nth-child(1) {{ width: 18%; }}
        th:nth-child(2), td:nth-child(2) {{ width: 62%; }}
        th:nth-child(3), td:nth-child(3) {{ width: 20%; }}
        tr:hover {{
            background: rgba(55, 65, 81, 0.5);
        }}
        .stacked-bars {{
            width: 100%;
        }}
        .progress-bar-small {{
            width: 100%;
            height: 20px;
            background: #4b5563;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            margin: 3px 0;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
        }}
        .progress-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            min-width: 40px;
        }}
        .progress-fill-zero {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding-left: 8px;
            color: #d1d5db;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }}
        .progress-fill.progress-blue {{
            background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
            color: white;
        }}
        .progress-fill.success-green {{
            background: linear-gradient(90deg, #28a745 0%, #1e7e34 100%);
            color: white;
        }}
        .status {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status.success {{
            background: #d4edda;
            color: #155724;
        }}
        .status.warning {{
            background: #fff3cd;
            color: #856404;
        }}
        .status.error {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status.error-critical {{
            background: #8b0000;
            color: white;
        }}
        /* Mini details (inline mini page) */
        .mini-link {{
            margin-left: 8px;
            font-size: 12px;
            color: #60a5fa;
            text-decoration: underline;
            cursor: pointer;
        }}
        /* Retailer name truncated to keep link visible */
        .retailer-name {{
            display: inline-block;
            max-width: 75%;
            vertical-align: middle;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .mini-details-row td {{
            background: #111827 !important;
        }}
        .mini-card {{
            display: flex;
            gap: 24px;
            align-items: center;
            padding: 10px 6px;
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
        .detail-btn {{
            background: #4f46e5;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
        }}
        .detail-btn:hover {{
            background: #3730a3;
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        .modal-content {{
            background-color: #1f2937;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 600px;
            color: white;
        }}
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .close:hover {{
            color: white;
        }}
        .detail-section {{
            margin: 15px 0;
            padding: 10px;
            background: #374151;
            border-radius: 6px;
        }}
        .history-day {{
            display: inline-block;
            width: 30px;
            height: 20px;
            margin: 2px;
            border-radius: 3px;
            text-align: center;
            font-size: 10px;
            line-height: 20px;
            color: white;
        }}
        .history-success {{ background: #10b981; }}
        .history-warning {{ background: #f59e0b; }}
        .history-error {{ background: #ef4444; }}
        .history-na {{ background: #6b7280; }}
        
        /* Pro visual refresh: palette, KPIs, sticky header, segmented filters, badges */
        :root {{
            --c-primary:#2563eb; --c-success:#10b981; --c-warning:#f59e0b; --c-error:#ef4444; --c-error-crit:#991b1b;
            --c-bg:#0f172a; --c-surface:#111827; --c-surface-2:#1f2937; --c-border:#334155; --c-text:#e5e7eb; --c-muted:#94a3b8;
            --radius:10px; --radius-badge:999px; --shadow-1:0 2px 6px rgba(0,0,0,.2); --shadow-2:0 8px 24px rgba(0,0,0,.35);
        }}
        body {{ background: var(--c-bg); color: var(--c-text); }}
        .container {{ background: var(--c-surface-2); box-shadow: var(--shadow-1); }}
        .header {{ background: #0b1220; border:1px solid var(--c-border); height:auto; padding: 12px 16px; }}
        .header-time {{ color: var(--c-muted); font-size: 12px; }}
        .table-container {{ background: var(--c-surface-2); border:1px solid var(--c-border); }}
        th {{ position: sticky; top: 0; z-index: 2; background: #111827; border-bottom: 1px solid var(--c-border); }}
        tr:hover {{ background: rgba(148,163,184,.08); }}
        /* KPI tiles */
        .kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; padding: 12px 0 4px; }}
        .kpi-card {{ background: #0b1220; border:1px solid var(--c-border); border-radius: var(--radius); padding: 10px 12px; box-shadow: var(--shadow-1); }}
        .kpi-card .kpi-label {{ color: var(--c-muted); font-size: 12px; font-weight: 600; }}
        .kpi-card .kpi-value {{ font-size: 20px; font-weight: 800; margin-top: 2px; }}
        .kpi-card.success .kpi-value {{ color: #34d399; }}
        .kpi-card.warning .kpi-value {{ color: #fbbf24; }}
        .kpi-card.error .kpi-value {{ color: #f87171; }}
        /* Segmented filters */
        .filters {{ background: transparent; border-bottom: none; padding: 12px 0 18px; }}
        .filter-buttons {{ border:1px solid var(--c-border); border-radius: 999px; padding: 6px; background: #0b1220; box-shadow: var(--shadow-1); }}
        .filter-btn {{ border-radius: 999px; padding: 8px 14px; box-shadow: none; border:1px solid transparent; background: transparent; color: var(--c-text); }}
        .filter-btn.active {{ background: #1e293b; border-color: var(--c-border); }}
        .btn-success.active {{ background: rgba(16,185,129,.15); color: #34d399; border-color: rgba(16,185,129,.35); }}
        .btn-warning.active {{ background: rgba(245,158,11,.15); color: #fbbf24; border-color: rgba(245,158,11,.35); }}
        .btn-error.active, .btn-error-critical.active {{ background: rgba(239,68,68,.15); color: #fca5a5; border-color: rgba(239,68,68,.35); }}
        /* Status badges */
        .status {{ border:1px solid rgba(255,255,255,.08); letter-spacing: .3px; }}
        .status.success {{ background: rgba(16,185,129,.12); color:#34d399; border-color: rgba(16,185,129,.35); }}
        .status.warning {{ background: rgba(245,158,11,.12); color:#fbbf24; border-color: rgba(245,158,11,.35); }}
        .status.error {{ background: rgba(239,68,68,.12); color:#fca5a5; border-color: rgba(239,68,68,.35); }}
        .status.error-critical {{ background: rgba(153,27,27,.35); color:#fecaca; border-color: rgba(252,165,165,.35); }}
        /* History chips */
        .history-day {{ border:1px solid rgba(255,255,255,.06); border-radius: 6px; }}
        /* Footer */
        .footer {{ margin-top: 14px; padding: 10px 14px; color: var(--c-muted); border-top: 1px solid var(--c-border); font-size: 12px; }}
        /* Visual alignment with spider-vision.data-solutions.com (CSS-only overrides) */
        body {{ background: radial-gradient(1200px 600px at -10% -10%, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.0) 60%), #1e2533; }}
        .container {{ background: #0f1720; border: 1px solid #2b3446; box-shadow: 0 8px 24px rgba(0,0,0,.35); }}
        .header {{ background: linear-gradient(180deg,#1a2231 0%, #151c28 100%); border: 1px solid #2b3446; border-radius: 10px; }}
        .header-time {{ color:#9fb0c7; font-weight:600; }}
        .filters {{ padding-top: 10px; }}
        .filter-buttons {{ background:#0e1622; border-color:#2b3446; }}
        .filter-btn {{ color:#c9d3e1; font-weight:600; }}
        .filter-btn:hover {{ background:#162131; border-color:#3a465c; }}
        .filter-btn.active {{ background:#192335; border-color:#3b4a63; box-shadow: inset 0 0 0 1px rgba(255,255,255,.03); }}
        table {{ background:#0f1720; }}
        th {{ background:#131a27; color:#b9c6d6; border-bottom:1px solid #2b3446; }}
        td {{ border-bottom:1px solid #1f2a3b; color:#e6eef8; }}
        tr:hover {{ background: rgba(59,73,99,.22); }}
        /* Column color bands similar to screenshot */
        tr.success td:not(:first-child) {{ background-color: rgba(16,185,129,.10); }}
        tr.warning td:not(:first-child) {{ background-color: rgba(245,158,11,.10); }}
        tr.error td:not(:first-child) {{ background-color: rgba(239,68,68,.10); }}
        tr.error_critical td:not(:first-child) {{ background-color: rgba(153,27,27,.18); }}
        /* Progress bars */
        .progress-bar-small {{ background:#263248; height:22px; border-radius: 6px; box-shadow: inset 0 2px 6px rgba(0,0,0,.45); }}
        .progress-fill.progress-blue {{ background: linear-gradient(90deg,#6ea8fe 0%, #4a6ff3 100%); }}
        .progress-fill.success-green {{ background: linear-gradient(90deg,#34d399 0%, #10b981 100%); }}
        .progress-fill, .progress-fill-zero {{ font-size:12px; }}
        /* Status badges like small rounded pills */
        .status {{ border-radius: 8px; padding: 6px 10px; font-weight:700; letter-spacing:.2px; }}
        .status.success {{ background:#0b3b2b; color:#82f3c2; border-color:#1e8a64; }}
        .status.warning {{ background:#3a2b06; color:#ffd36e; border-color:#a57913; }}
        .status.error {{ background:#3b1113; color:#ff9aa2; border-color:#b23a41; }}
        .status.error-critical {{ background:#3a0d0d; color:#ffd1d1; border-color:#a33; }}
        /* History chips: vivid with white text */
        .history-day {{ min-width: 44px; height: 22px; line-height: 22px; font-weight: 700; font-size: 11px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.08), 0 1px 2px rgba(0,0,0,.25); }}
        .history-success {{ background:#16a34a; }}
        .history-warning {{ background:#d97706; }}
        .history-error {{ background:#b91c1c; }}
        .history-na {{ background:#334155; }}
        /* Mini details card */
        .mini-details-row td {{ background:#0b1220 !important; }}
        .mini-card {{ padding: 10px 10px; border:1px solid #2b3446; border-radius:10px; background:#0f1720; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <div class="logo">
                    <img src="{logo_base64}" alt="SpiderVision Logo">
                </div>
            </div>
            <div class="header-time">{current_time}</div>
        </div>
        
        
        <div class="filters">
            <div class="filter-buttons">
                <button class="filter-btn btn-all active" onclick="filterTable('all', this)">Tous ({total_count})</button>
                <button class="filter-btn btn-success" onclick="filterTable('success', this)">Succès ({stats['Succès']})</button>
                <button class="filter-btn btn-warning" onclick="filterTable('warning', this)">Warning ({stats['Warning']})</button>
                <button class="filter-btn btn-error" onclick="filterTable('error', this)">Erreur ({stats['Erreur']})</button>
                <button class="filter-btn btn-error-critical" onclick="filterTable('error-critical', this)">Erreur! ({stats['Erreur!']})</button>
            </div>
        </div>
        
        <div class="table-container">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Enseigne</th>
                        <th>
                            Progress & Success (%)
                            <span class="info-icon" title="Bleu: % de magasins crawlés | Vert: % de magasins avec contenu">ℹ️</span>
                        </th>
                        <th>Statut</th>
                    </tr>
                </thead>
                <tbody>"""
    
    # Ajouter les lignes de données
    for retailer in retailers_data:
        global_class = get_status_class(retailer['global_status']).replace('-', '_')
        status_class = get_status_class(retailer['global_status'])
        progress_class = get_status_class(retailer['progress_status'])
        success_class = get_status_class(retailer['success_status'])
        # Préparer les données d'historique pour JavaScript
        history_data = []
        for i in range(6):  # day0 à day5
            day_key = f'day{i}'
            if day_key in retailer and retailer[day_key]:
                try:
                    day_data = ast.literal_eval(retailer[day_key])
                    if isinstance(day_data, dict) and 'successPercent' in day_data:
                        history_data.append(day_data['successPercent'])
                    else:
                        history_data.append(None)
                except:
                    history_data.append(None)
            else:
                history_data.append(None)
        
        history_json = json.dumps(history_data)
        name_attr = retailer['name'].replace('"', '&quot;')
        
        html_content += f"""
                    <tr class=\"{global_class}\" data-status=\"{retailer['global_status']}\" data-history='{history_json}'>
                        <td><strong class=\"retailer-name\">{retailer['name']}</strong> <a class=\"mini-link\" href=\"javascript:void(0)\" onclick=\"toggleMini(this)\">Voir statuts</a></td>
                        <td>{create_stacked_progress_bars(retailer['progress'], retailer['progress_status'], retailer['success'], retailer['success_status'])}</td>
                        <td><span class=\"status {status_class}\">{retailer['global_status']}</span></td>
                    </tr>
                    <tr class=\"mini-details-row hidden\">
                        <td colspan=\"3\">
                            <div class=\"mini-card\">\n                                <div><strong>Historique (Success 6j):</strong> <span class=\"history-line\"></span></div>
                                <div><strong>Progress:</strong> <span class=\"status {progress_class}\">{retailer['progress']:.1f}% ({retailer['progress_status']})</span></div>
                                <div><strong>Success:</strong> <span class=\"status {success_class}\">{retailer['success']:.1f}% ({retailer['success_status']})</span></div>
                            </div>
                        </td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        <div class="footer">Rapport SpiderVision Live • Généré le: {current_time} • Source: spider_vision_overview_current.csv</div>
        </div>

        <script>
        function filterTable(filter, el) {
            const rows = document.querySelectorAll('#dataTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Reset button states
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Set active button
            if (el) { el.classList.add('active'); }
            
            rows.forEach(row => {
                const isMini = row.classList.contains('mini-details-row');
                if (filter === 'all') {
                    // Show all rows; mini rows respect their own hidden class
                    row.style.display = isMini && row.classList.contains('hidden') ? 'none' : '';
                } else {
                    if (isMini) {
                        // Mini row visibility depends on its parent row and hidden state
                        const parent = row.previousElementSibling;
                        const pStatus = parent ? parent.getAttribute('data-status') : null;
                        const pClass = pStatus ? getStatusClass(pStatus) : '';
                        const parentMatches = (filter === pClass) || (filter === 'error-critical' && pStatus === 'Erreur!');
                        row.style.display = parentMatches && !row.classList.contains('hidden') ? '' : 'none';
                    } else {
                        const status = row.getAttribute('data-status');
                        const statusClass = getStatusClass(status);
                        if (filter === statusClass || (filter === 'error-critical' && status === 'Erreur!')) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    }
                }
            });
        }
        
        function getStatusClass(status) {
            if (status === 'Succès') return 'success';
            if (status === 'Warning') return 'warning';
            if (status === 'Erreur!') return 'error-critical';
            if (status === 'Erreur') return 'error';
            return '';
        }
        // Status class for history successPercent using same rules as day J
        function getHistoryStatusClass(percent) {
            if (!isFinite(percent)) return 'history-na';
            if (percent === 0) return 'history-error'; // Erreur!
            if (percent >= 95) return 'history-success';
            if (percent >= 90) return 'history-warning';
            return 'history-error';
        }
        
        function toggleMini(el) {
            const row = el.closest('tr');
            const details = row.nextElementSibling;
            if (details && details.classList.contains('mini-details-row')) {
                // Toggle logical hidden class
                details.classList.toggle('hidden');
                // Ensure inline display matches the new state (overrides previous filter inline style)
                if (details.classList.contains('hidden')) {
                    details.style.display = 'none';
                } else {
                    details.style.display = '';
                }
                // Render history on first open
                const historySpan = details.querySelector('.history-line');
                if (historySpan && !historySpan.dataset.rendered) {
                    try {
                        const histStr = row.getAttribute('data-history') || '[]';
                        const hist = JSON.parse(histStr);
                        const pieces = (Array.isArray(hist) ? hist : []).map((v, idx) => {
                            if (v === null || v === undefined || Number.isNaN(v)) {
                                return '<span class="history-day history-na" title="Jour ' + idx + ': N/A">—</span>';
                            }
                            const n = Math.round(Number(v));
                            const cls = getHistoryStatusClass(n);
                            return '<span class="history-day ' + cls + '" title="Jour ' + idx + ': ' + n + '%">' + n + '%</span>';
                        });
                        historySpan.innerHTML = pieces.join('');
                    } catch (e) {
                        historySpan.textContent = '—';
                    }
                    historySpan.dataset.rendered = '1';
                }
            }
        }
        
    </script>
</body>
</html>"""
    
    # Sauvegarder le fichier
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Nouveau rapport généré: {filename}")
    
    # Mettre à jour automatiquement index.html avec le lien du nouveau rapport
    try:
        from update_index_link import auto_update_index
        auto_update_index()
    except Exception as e:
        print(f"⚠️ Impossible de mettre à jour index.html: {e}")
    
    return filename

if __name__ == "__main__":
    generate_new_report()
