"""Dependency injection container for the dealer-report application."""
import logging
import os
from dependency_injector import containers, providers
from dotenv import load_dotenv

from cli.repository.MockDataRepository import MockDataRepository
from cli.repository.WebDataRepository import WebDataRepository
from cli.services.ReportService import ReportService
from cli.services.GcsPublisher import GcsPublisher
from cli.services.TeamsNotifier import TeamsNotifier

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""
    
    # Configuration
    logging = providers.Resource(
        logging.basicConfig,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Spider Vision configuration
    spider_vision_url = providers.Object(
        os.getenv('SPIDER_VISION_URL', 'https://spider-vision.data-solutions.com/')
    )
    
    spider_vision_username = providers.Object(
        os.getenv('SPIDER_VISION_USERNAME', '')
    )
    
    spider_vision_password = providers.Object(
        os.getenv('SPIDER_VISION_PASSWORD', '')
    )
    
    # Repository for retrieving data (using mock data for now)
    mock_data_repository = providers.Singleton(
        MockDataRepository
    )
    
    # Repository for retrieving real data from Spider Vision
    web_data_repository = providers.Singleton(
        WebDataRepository,
        base_url=spider_vision_url,
        username=spider_vision_username,
        password=spider_vision_password
    )
    
    # GCP configuration
    gcp_project = providers.Object(
        os.getenv('GCP_PROJECT', 'my-gcp-project')
    )
    
    gcs_bucket = providers.Object(
        os.getenv('GCS_BUCKET', 'my-analytics-bucket')
    )
    
    google_application_credentials = providers.Object(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    )
    
    # Teams configuration
    teams_webhook_url = providers.Object(
        os.getenv('TEAMS_WEBHOOK_URL', '')
    )
    
    teams_default_message = providers.Object(
        os.getenv('TEAMS_DEFAULT_MESSAGE', 'Bonjour, voici le rapport du jour.')
    )
    
    # Application configuration
    reports_dir = providers.Object(
        os.getenv('REPORTS_DIR', './reports')
    )
    
    timezone = providers.Object(
        os.getenv('TZ', 'Europe/Paris')
    )
    
    include_successes = providers.Object(
        os.getenv('INCLUDE_SUCCESSES', 'false').lower() == 'true'
    )
    
    gcs_latest_html_path = providers.Object(
        os.getenv('GCS_LATEST_HTML_PATH', 'reports/daily/dealer-report-latest.html')
    )
    
    # App config dictionary for CLI usage
    app_config = providers.Dict(
        GCS_LATEST_HTML_PATH=gcs_latest_html_path,
        REPORTS_DIR=reports_dir,
        TZ=timezone,
        INCLUDE_SUCCESSES=include_successes
    )
    
    # Services
    report_service = providers.Singleton(
        ReportService,
        repository=web_data_repository,  # Utiliser les vraies données Spider Vision
        output_dir=reports_dir,
        tz=timezone,
        include_successes=include_successes
    )
    
    gcs_publisher = providers.Singleton(
        GcsPublisher,
        default_bucket=gcs_bucket,
        gcp_project=gcp_project
    )
    
    teams_notifier = providers.Singleton(
        TeamsNotifier,
        webhook_url=teams_webhook_url,
        default_message=teams_default_message
    )


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from some libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)


def get_container() -> Container:
    """Get configured container instance."""
    setup_logging()
    container = Container()
    return container
