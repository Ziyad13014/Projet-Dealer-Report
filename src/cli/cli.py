"""Click CLI for dealer-report application."""
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import click
from cli.ioc import get_container

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Daily dealer anomaly report CLI (MySQL -> CSV/HTML -> GCS -> Teams)."""
    pass


@cli.command()
@click.option('--date-from', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='Start date (YYYY-MM-DD). Defaults to today.')
@click.option('--date-to', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='End date (YYYY-MM-DD). Defaults to today.')
@click.option('--dealer', type=str, help='Filter by specific retailer name.')
@click.option('--fmt', type=click.Choice(['csv', 'html', 'both']), default='both',
              help='Output format. Default: both')
def generate_dealer_report(date_from: Optional[datetime], date_to: Optional[datetime], 
                          dealer: Optional[str], fmt: str):
    """Generate dealer anomaly report from MySQL data.
    
    Produces CSV and/or HTML reports based on retailer rules for success rate
    and progress at 09:30 Europe/Paris. Reports show anomalies by default,
    with optional successes section if configured.
    
    Examples:
    
        # Generate today's report in both formats
        dealer-report generate_dealer_report
        
        # Generate report for specific date range
        dealer-report generate_dealer_report --date-from 2024-01-01 --date-to 2024-01-31
        
        # Generate HTML report for specific retailer
        dealer-report generate_dealer_report --dealer Carrefour --fmt html
    """
    try:
        container = get_container()
        report_service = container.report_service()
        
        # Convert datetime to date
        date_from_val = date_from.date() if date_from else None
        date_to_val = date_to.date() if date_to else None
        
        # Validate date range
        if date_from_val and date_to_val and date_from_val > date_to_val:
            raise click.BadParameter("date-from must be <= date-to")
        
        # Generate report
        output_path = report_service.generate_dealer_report(
            date_from=date_from_val,
            date_to=date_to_val,
            dealer=dealer,
            fmt=fmt
        )
        
        click.echo(f"Report generated: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise click.ClickException(f"Report generation failed: {e}")


@cli.command()
@click.option('--path', type=click.Path(exists=True, path_type=Path), required=True,
              help='Path to the file to upload.')
@click.option('--bucket', type=str, help='GCS bucket name (uses default if not specified).')
@click.option('--dst', type=str, help='Destination blob path in GCS. Auto-generated if not specified.')
def publish_report(path: Path, bucket: Optional[str], dst: Optional[str]):
    """Upload report to Google Cloud Storage.
    
    Uploads the specified file to GCS and returns the gs:// URL.
    Also updates the fixed "latest" path for consistent access.
    
    Examples:
    
        # Upload with auto-generated destination
        dealer-report publish_report --path ./reports/dealer-report-20240101.html
        
        # Upload to specific bucket and path
        dealer-report publish_report --path ./report.html --bucket my-bucket --dst reports/custom/report.html
    """
    try:
        container = get_container()
        gcs_publisher = container.gcs_publisher()
        app_config = container.app_config()
        
        # Generate destination path if not provided
        if not dst:
            now = datetime.utcnow()
            filename = path.name
            dst = f"reports/{now.year:04d}/{now.month:02d}/{now.day:02d}/{filename}"
        
        # Upload file
        gs_url = gcs_publisher.upload(str(path), dst, bucket)
        click.echo(f"Uploaded: {gs_url}")
        
        # Update latest path if it's an HTML file
        if path.suffix.lower() == '.html':
            latest_path = app_config['GCS_LATEST_HTML_PATH']
            latest_url = gcs_publisher.update_latest(dst, latest_path, bucket)
            click.echo(f"Latest URL: {latest_url}")
        
    except Exception as e:
        logger.error(f"Failed to publish report: {e}")
        raise click.ClickException(f"Report publishing failed: {e}")


@cli.command()
@click.option('--url', type=str, required=True,
              help='URL to include in the Teams message (typically the GCS report URL).')
@click.option('--message', type=str, help='Custom message text (uses default if not specified).')
@click.option('--channel-webhook', type=str, help='Override Teams webhook URL.')
def push_notification_on_teams(url: str, message: Optional[str], channel_webhook: Optional[str]):
    """Post notification message to Microsoft Teams.
    
    Sends a message with the report URL to the configured Teams channel
    via webhook. Includes retry logic for reliability.
    
    Examples:
    
        # Send notification with default message
        dealer-report push_notification_on_teams --url "https://storage.googleapis.com/bucket/report.html"
        
        # Send with custom message
        dealer-report push_notification_on_teams --url "gs://bucket/report.html" --message "Rapport urgent disponible"
        
        # Send to different channel
        dealer-report push_notification_on_teams --url "gs://bucket/report.html" --channel-webhook "https://..."
    """
    try:
        container = get_container()
        teams_notifier = container.teams_notifier()
        
        # Validate URL
        if not url.strip():
            raise click.BadParameter("URL cannot be empty")
        
        # Send notification
        success = teams_notifier.send_notification(
            url=url,
            message=message,
            webhook_url=channel_webhook
        )
        
        if success:
            click.echo("Teams notification sent successfully")
        else:
            raise click.ClickException("Failed to send Teams notification")
        
    except Exception as e:
        logger.error(f"Failed to send Teams notification: {e}")
        raise click.ClickException(f"Teams notification failed: {e}")


@cli.command()
@click.option('--email', type=str, help='Email for SpiderVision authentication (uses .env if not specified).')
@click.option('--password', type=str, help='Password for SpiderVision authentication (uses .env if not specified).')
@click.option('--format', type=click.Choice(['csv', 'excel', 'html']), default='csv',
              help='Output format. Default: csv')
@click.option('--output', type=str, help='Output filename (auto-generated if not specified).')
def fetch_overview(email: Optional[str], password: Optional[str], format: str, output: Optional[str]):
    """Fetch overview data from SpiderVision API and export to CSV/Excel.
    
    Authenticates with SpiderVision API using JWT, retrieves overview data,
    and exports it to CSV or Excel format.
    
    Examples:
    
        # Fetch and export to CSV (using .env credentials)
        dealer-report fetch_overview
        
        # Fetch and export to Excel
        dealer-report fetch_overview --format excel
        
        # Use custom credentials and output file
        dealer-report fetch_overview --email user@example.com --password secret --output my_data.csv
    """
    try:
        from cli.services.auth import SpiderVisionAuth
        from cli.services.data import SpiderVisionData
        from cli.services.export import DataExporter
        
        # Initialize services
        auth = SpiderVisionAuth()
        data_service = SpiderVisionData()
        exporter = DataExporter()
        
        # Override credentials if provided
        if email:
            auth.email = email
        if password:
            auth.password = password
        
        # Authenticate
        click.echo("🔐 Authentification en cours...")
        token = auth.login()
        click.echo("✅ Authentification réussie")
        
        # Fetch data
        click.echo("📊 Récupération des données overview...")
        overview_data = data_service.get_overview(token)
        click.echo(f"✅ Données récupérées ({len(str(overview_data))} caractères)")
        
        # Export data
        click.echo(f"💾 Export en format {format.upper()}...")
        if output:
            if format == 'excel' and not output.endswith(('.xlsx', '.xls')):
                output += '.xlsx'
            elif format == 'csv' and not output.endswith('.csv'):
                output += '.csv'
            elif format == 'html' and not output.endswith('.html'):
                output += '.html'
            
            if format == 'excel':
                filepath = exporter.save_to_excel(overview_data, output)
            elif format == 'html':
                filepath = exporter.save_to_html(overview_data, output)
            else:
                filepath = exporter.save_to_csv(overview_data, output)
        else:
            filepath = exporter.save_overview_data(overview_data, format)
        
        click.echo(f"✅ Données exportées vers: {filepath}")
        
    except Exception as e:
        logger.error(f"Failed to fetch overview: {e}")
        raise click.ClickException(f"Overview fetch failed: {e}")


if __name__ == '__main__':
    cli()
