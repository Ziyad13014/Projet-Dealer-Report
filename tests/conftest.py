"""Pytest configuration and fixtures for dealer-report tests."""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import date, datetime
from cli.repository.IncidentRepository import RetailerRule


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value.__exit__.return_value = None
    return connection


@pytest.fixture
def sample_retailer_rules():
    """Sample retailer rules for testing."""
    return [
        RetailerRule(
            retailer="Carrefour",
            min_success_rate=0.95,
            min_progress_0930=0.10,
            include_successes=False
        ),
        RetailerRule(
            retailer="Intermarché",
            min_success_rate=0.90,
            min_progress_0930=0.10,
            include_successes=False
        ),
        RetailerRule(
            retailer="Auchan",
            min_success_rate=0.90,
            min_progress_0930=None,
            include_successes=True
        )
    ]


@pytest.fixture
def mock_gcs_client():
    """Mock Google Cloud Storage client."""
    client = Mock()
    bucket = Mock()
    blob = Mock()
    
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    bucket.copy_blob.return_value = None
    blob.upload_from_file.return_value = None
    
    return client


@pytest.fixture
def mock_requests():
    """Mock requests module."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    
    mock_requests = Mock()
    mock_requests.post.return_value = mock_response
    
    return mock_requests
