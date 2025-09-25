"""Service for generating dealer anomaly reports in CSV and HTML formats."""
import logging
import os
import csv
from datetime import date, time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

from cli.repository.WebDataRepository import WebDataRepository

logger = logging.getLogger(__name__)


@dataclass
class ReportItem:
    """Single report item representing a rule evaluation."""
    retailer: str
    rule_type: str  # 'crawling_rate' or 'content_rate'
    threshold_success: float
    threshold_warning: float
    actual_value: float
    status: str  # 'success', 'warning', 'error'
    details: dict
    message: str


class ReportService:
    """Service for generating dealer anomaly reports."""
    
    def __init__(self, repository, output_dir: str, tz: str = "Europe/Paris", include_successes: bool = False):
        self.repository = repository
        self.output_dir = output_dir
        self.tz = tz
        self.include_successes = include_successes
        self.logger = logging.getLogger(__name__)
        
        # Créer le dossier de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_dealer_report(
        self, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None,
        dealer: Optional[str] = None,
        fmt: str = "both"
    ) -> str:
        """Generate dealer anomaly report.
        
        Args:
            date_from: Start date (defaults to today)
            date_to: End date (defaults to today)
            dealer: Optional retailer filter
            fmt: Output format ('csv', 'html', or 'both')
            
        Returns:
            Path to the generated file (HTML path if fmt='both')
        """
        # Default dates to today in local timezone
        if date_from is None:
            date_from = date.today()
        if date_to is None:
            date_to = date.today()
            
        logger.info(f"Generating report for {date_from} to {date_to}, dealer={dealer}, format={fmt}")
        
        # Get retailer rules
        rules = self.repository.get_rules(dealer)
        if not rules:
            logger.warning(f"No retailer rules found for dealer filter: {dealer}")
            
        # Generate report items
        report_items = self._generate_report_items(rules, date_from, date_to)
        
        # Generate output files
        timestamp = date_from.strftime("%Y%m%d")
        if date_from != date_to:
            timestamp += f"-{date_to.strftime('%Y%m%d')}"
            
        csv_path = None
        html_path = None
        
        if fmt in ('csv', 'both'):
            csv_path = Path(self.output_dir) / f"dealer-report-{timestamp}.csv"
            self._write_csv(report_items, csv_path, date_from, date_to)
            
        if fmt in ('html', 'both'):
            html_path = Path(self.output_dir) / f"dealer-report-{timestamp}.html"
            self._write_html(report_items, html_path, date_from, date_to)
            
        # Return appropriate path
        if fmt == 'csv':
            return str(csv_path)
        elif fmt == 'html':
            return str(html_path)
        else:  # both
            return str(html_path)
    
    def _generate_report_items(self, rules, date_from: date, date_to: date) -> List[ReportItem]:
        """Generate report items by evaluating rules."""
        items = []
        
        for rule in rules:
            # Check crawling rate rule
            if rule.get('min_crawling_rate') is not None:
                counters = self.repository.get_crawling_counters(rule['retailer_name'], date_from, date_to)
                crawling_count = counters['crawling_count']
                total_count = counters['total_count']
                
                if total_count == 0:
                    crawling_rate = 0.0
                else:
                    crawling_rate = (crawling_count / total_count) * 100
                
                # Create report item for crawling rate
                item = ReportItem(
                    retailer=rule['retailer_name'],
                    rule_type="crawling_rate",
                    threshold_success=rule['min_crawling_rate'],
                    threshold_warning=rule['min_crawling_rate_warning'],
                    actual_value=crawling_rate,
                    status=self._get_status(crawling_rate, rule['min_crawling_rate'], rule['min_crawling_rate_warning']),
                    details={
                        'crawling_count': crawling_count,
                        'total_count': total_count,
                        'period_days': (date_to - date_from).days + 1
                    },
                    message=""
                )
                items.append(item)
                
                logger.debug(f"Crawling rate for {rule['retailer_name']}: {crawling_rate:.1f}% "
                           f"({crawling_count}/{total_count}), threshold: {rule['min_crawling_rate']}%")
            
            # Check content rate rule
            if rule.get('min_content_rate') is not None:
                counters = self.repository.get_content_counters(rule['retailer_name'], date_from, date_to)
                content_count = counters['content_count']
                total_count = counters['total_count']
                
                if total_count == 0:
                    content_rate = 0.0
                else:
                    content_rate = (content_count / total_count) * 100
                
                # Create report item for content rate
                item = ReportItem(
                    retailer=rule['retailer_name'],
                    rule_type="content_rate",
                    threshold_success=rule['min_content_rate'],
                    threshold_warning=rule['min_content_rate_warning'],
                    actual_value=content_rate,
                    status=self._get_status(content_rate, rule['min_content_rate'], rule['min_content_rate_warning']),
                    details={
                        'content_count': content_count,
                        'total_count': total_count,
                        'period_days': (date_to - date_from).days + 1
                    },
                    message=""
                )
                items.append(item)
        
        # Sort items: errors first (by retailer), then warnings, then successes (by retailer)
        items.sort(key=lambda x: (x.status != 'success', x.retailer))
        return items
    
    def _get_status(self, actual_value: float, threshold_success: float, threshold_warning: float) -> str:
        """Get the status of a report item."""
        if actual_value >= threshold_success:
            return 'success'
        elif actual_value >= threshold_warning:
            return 'warning'
        else:
            return 'error'
    
    def _format_percentage(self, value: float) -> str:
        """Format a decimal as a percentage with at most one decimal place."""
        percentage = value
        if percentage == int(percentage):
            return f"{int(percentage)}%"
        else:
            return f"{percentage:.1f}%"
    
    def _write_csv(self, items: List[ReportItem], path: Path, date_from: date, date_to: date):
        """Write report items to CSV file."""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'retailer', 'rule', 'status', 'measured', 'threshold_success', 'threshold_warning'])
            
            date_range = f"{date_from}" if date_from == date_to else f"{date_from} to {date_to}"
            
            for item in items:
                writer.writerow([
                    date_range,
                    item.retailer,
                    item.rule_type,
                    item.status,
                    f"{item.actual_value:.4f}",
                    f"{item.threshold_success:.4f}",
                    f"{item.threshold_warning:.4f}"
                ])
        
        logger.info(f"CSV report written to {path}")
    
    def _write_html(self, items: List[ReportItem], path: Path, date_from: date, date_to: date):
        """Write report items to HTML file."""
        date_range = f"{date_from}" if date_from == date_to else f"{date_from} to {date_to}"
        
        # Separate errors, warnings and successes
        errors = [item for item in items if item.status == 'error']
        warnings = [item for item in items if item.status == 'warning']
        successes = [item for item in items if item.status == 'success']
        
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Dealer - {date_range}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007acc;
            padding-bottom: 10px;
        }}
        .meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #444;
            margin-bottom: 15px;
        }}
        .item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            font-family: monospace;
        }}
        .error {{
            background-color: #fff2f2;
            border-left: 4px solid #e74c3c;
        }}
        .warning {{
            background-color: #ffffe0;
            border-left: 4px solid #f7dc6f;
        }}
        .success {{
            background-color: #f2fff2;
            border-left: 4px solid #27ae60;
        }}
        .no-items {{
            color: #666;
            font-style: italic;
            padding: 20px;
            text-align: center;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Rapport Dealer - {date_range}</h1>
        <div class="meta">
            Généré le {date.today()} • Timezone: {self.tz}
        </div>
        
        <div class="section">
            <h2>⚠️ Erreurs</h2>
            {self._format_items_html(errors, 'error')}
        </div>
        
        {self._format_warnings_section(warnings) if warnings else ''}
        
        {self._format_successes_section(successes) if successes else ''}
    </div>
</body>
</html>"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report written to {path}")
    
    def _format_items_html(self, items: List[ReportItem], item_type: str) -> str:
        """Format report items as HTML."""
        if not items:
            return f'<div class="item {item_type}">Aucun élément à afficher.</div>'
        
        items_html = []
        for item in items:
            if item.rule_type == "crawling_rate":
                message = f"{item.retailer}: crawling rate = {self._format_percentage(item.actual_value)} (threshold {self._format_percentage(item.threshold_success)}, warning {self._format_percentage(item.threshold_warning)})"
            elif item.rule_type == "content_rate":
                message = f"{item.retailer}: content rate = {self._format_percentage(item.actual_value)} (threshold {self._format_percentage(item.threshold_success)}, warning {self._format_percentage(item.threshold_warning)})"
            else:
                message = f"{item.retailer}: {item.rule_type} = {self._format_percentage(item.actual_value)}"
            
            items_html.append(f'<div class="item {item_type}">{message}</div>')
        
        return '\n'.join(items_html)
    
    def _format_warnings_section(self, warnings: List[ReportItem]) -> str:
        """Render the warnings section if there are any."""
        if not warnings:
            return ''
        
        return f"""
        <div class="section">
            <h2>⚠️ Avertissements</h2>
            {self._format_items_html(warnings, 'warning')}
        </div>"""
    
    def _format_successes_section(self, successes: List[ReportItem]) -> str:
        """Render the successes section if there are any."""
        if not successes:
            return ''
        
        return f"""
        <div class="section">
            <h2>✅ Succès</h2>
            {self._format_items_html(successes, 'success')}
        </div>"""
