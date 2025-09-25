"""CLI smoke tests to verify command availability and help outputs."""
import pytest
from click.testing import CliRunner
from cli.cli import cli


class TestCLIHelp:
    """Test CLI help outputs and command availability."""
    
    def test_main_help(self):
        """Test main CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'Daily dealer anomaly report CLI' in result.output
        assert 'generate_dealer_report' in result.output
        assert 'publish_report' in result.output
        assert 'push_notification_on_teams' in result.output
    
    def test_generate_dealer_report_help(self):
        """Test generate_dealer_report command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate_dealer_report', '--help'])
        
        assert result.exit_code == 0
        assert 'Generate dealer anomaly report from MySQL data' in result.output
        assert '--date-from' in result.output
        assert '--date-to' in result.output
        assert '--dealer' in result.output
        assert '--fmt' in result.output
        assert 'csv' in result.output
        assert 'html' in result.output
        assert 'both' in result.output
    
    def test_publish_report_help(self):
        """Test publish_report command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['publish_report', '--help'])
        
        assert result.exit_code == 0
        assert 'Upload report to Google Cloud Storage' in result.output
        assert '--path' in result.output
        assert '--bucket' in result.output
        assert '--dst' in result.output
        assert 'required' in result.output  # --path is required
    
    def test_push_notification_on_teams_help(self):
        """Test push_notification_on_teams command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['push_notification_on_teams', '--help'])
        
        assert result.exit_code == 0
        assert 'Post notification message to Microsoft Teams' in result.output
        assert '--url' in result.output
        assert '--message' in result.output
        assert '--channel-webhook' in result.output
        assert 'required' in result.output  # --url is required
    
    def test_version_option(self):
        """Test version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert '0.1.0' in result.output
    
    def test_invalid_command(self):
        """Test invalid command handling."""
        runner = CliRunner()
        result = runner.invoke(cli, ['invalid_command'])
        
        assert result.exit_code != 0
        assert 'No such command' in result.output
    
    def test_generate_dealer_report_invalid_format(self):
        """Test generate_dealer_report with invalid format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate_dealer_report', '--fmt', 'invalid'])
        
        assert result.exit_code != 0
        assert 'Invalid value for' in result.output or 'invalid choice' in result.output.lower()
    
    def test_generate_dealer_report_invalid_date(self):
        """Test generate_dealer_report with invalid date format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate_dealer_report', '--date-from', 'invalid-date'])
        
        assert result.exit_code != 0
        assert 'Invalid value for' in result.output or 'does not match' in result.output
    
    def test_publish_report_missing_path(self):
        """Test publish_report without required --path option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['publish_report'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    def test_push_notification_missing_url(self):
        """Test push_notification_on_teams without required --url option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['push_notification_on_teams'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()


class TestCLIIntegration:
    """Integration tests for CLI commands (with mocking)."""
    
    @pytest.fixture
    def mock_container(self, mocker):
        """Mock the DI container and its services."""
        mock_container = mocker.Mock()
        mock_report_service = mocker.Mock()
        mock_gcs_publisher = mocker.Mock()
        mock_teams_notifier = mocker.Mock()
        mock_app_config = {'GCS_LATEST_HTML_PATH': 'reports/daily/latest.html'}
        
        mock_container.report_service.return_value = mock_report_service
        mock_container.gcs_publisher.return_value = mock_gcs_publisher
        mock_container.teams_notifier.return_value = mock_teams_notifier
        mock_container.app_config.return_value = mock_app_config
        
        mocker.patch('cli.cli.get_container', return_value=mock_container)
        return mock_container
    
    def test_generate_dealer_report_success(self, mock_container):
        """Test successful report generation."""
        mock_container.report_service.return_value.generate_dealer_report.return_value = '/tmp/report.html'
        
        runner = CliRunner()
        result = runner.invoke(cli, ['generate_dealer_report', '--fmt', 'html'])
        
        assert result.exit_code == 0
        assert 'Report generated: /tmp/report.html' in result.output
        mock_container.report_service.return_value.generate_dealer_report.assert_called_once()
    
    def test_publish_report_success(self, mock_container, tmp_path):
        """Test successful report publishing."""
        # Create a temporary file
        test_file = tmp_path / "test_report.html"
        test_file.write_text("<html>Test</html>")
        
        mock_container.gcs_publisher.return_value.upload.return_value = 'gs://bucket/report.html'
        mock_container.gcs_publisher.return_value.update_latest.return_value = 'gs://bucket/latest.html'
        
        runner = CliRunner()
        result = runner.invoke(cli, ['publish_report', '--path', str(test_file)])
        
        assert result.exit_code == 0
        assert 'Uploaded: gs://bucket/report.html' in result.output
        assert 'Latest URL: gs://bucket/latest.html' in result.output
    
    def test_push_notification_success(self, mock_container):
        """Test successful Teams notification."""
        mock_container.teams_notifier.return_value.send_notification.return_value = True
        
        runner = CliRunner()
        result = runner.invoke(cli, ['push_notification_on_teams', '--url', 'https://example.com/report.html'])
        
        assert result.exit_code == 0
        assert 'Teams notification sent successfully' in result.output
        mock_container.teams_notifier.return_value.send_notification.assert_called_once_with(
            url='https://example.com/report.html',
            message=None,
            webhook_url=None
        )
