"""Unit tests for business logic and rules evaluation."""
import pytest
from unittest.mock import Mock, patch
from datetime import date, time
from pathlib import Path
import tempfile
import os

from cli.repository.IncidentRepository import IncidentRepository, RetailerRule
from cli.services.ReportService import ReportService, ReportItem


class TestIncidentRepository:
    """Test IncidentRepository business logic."""
    
    def test_get_success_counters_normal_case(self, mock_db_connection):
        """Test success rate calculation with normal data."""
        # Setup mock cursor response
        cursor = mock_db_connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = {'success_count': 8, 'total_count': 10}
        
        repo = IncidentRepository(mock_db_connection)
        success_count, total_count = repo.get_success_counters(
            'Carrefour', date(2024, 1, 1), date(2024, 1, 1)
        )
        
        assert success_count == 8
        assert total_count == 10
        
        # Verify SQL was called with correct parameters
        cursor.execute.assert_called_once()
        args = cursor.execute.call_args[0]
        assert 'success' in args[0]  # SQL contains success status
        assert args[1] == ('Carrefour', date(2024, 1, 1), date(2024, 1, 1))
    
    def test_get_success_counters_zero_total(self, mock_db_connection):
        """Test success rate calculation when no data exists."""
        cursor = mock_db_connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = {'success_count': 0, 'total_count': 0}
        
        repo = IncidentRepository(mock_db_connection)
        success_count, total_count = repo.get_success_counters(
            'NonExistent', date(2024, 1, 1), date(2024, 1, 1)
        )
        
        assert success_count == 0
        assert total_count == 0
    
    def test_get_progress_at_with_plan(self, mock_db_connection):
        """Test progress calculation when runs_plan exists."""
        cursor = mock_db_connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.side_effect = [
            {'expected_total': 5},  # runs_plan query
            {'completed_count': 2}  # completed runs query
        ]
        
        repo = IncidentRepository(mock_db_connection)
        completed, expected = repo.get_progress_at(
            'Carrefour', date(2024, 1, 1), time(9, 30)
        )
        
        assert completed == 2
        assert expected == 5
        
        # Should have made 2 SQL calls
        assert cursor.execute.call_count == 2
    
    def test_get_progress_at_fallback_to_runs_count(self, mock_db_connection):
        """Test progress calculation fallback when no runs_plan exists."""
        cursor = mock_db_connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.side_effect = [
            None,  # No runs_plan
            {'total_count': 3},  # Fallback count
            {'completed_count': 1}  # Completed runs
        ]
        
        repo = IncidentRepository(mock_db_connection)
        completed, expected = repo.get_progress_at(
            'Carrefour', date(2024, 1, 1), time(9, 30)
        )
        
        assert completed == 1
        assert expected == 3
        
        # Should have made 3 SQL calls (plan, fallback, completed)
        assert cursor.execute.call_count == 3
    
    def test_get_progress_at_no_expected_total(self, mock_db_connection):
        """Test progress calculation when expected total cannot be determined."""
        cursor = mock_db_connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.side_effect = [
            None,  # No runs_plan
            {'total_count': 0},  # No fallback data
            {'completed_count': 0}  # No completed runs
        ]
        
        repo = IncidentRepository(mock_db_connection)
        completed, expected = repo.get_progress_at(
            'Carrefour', date(2024, 1, 1), time(9, 30)
        )
        
        assert completed == 0
        assert expected is None


class TestReportService:
    """Test ReportService report generation logic."""
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', False)
            
            assert service._format_percentage(0.95) == "95%"
            assert service._format_percentage(0.951) == "95.1%"
            assert service._format_percentage(0.9567) == "95.7%"
            assert service._format_percentage(1.0) == "100%"
            assert service._format_percentage(0.0) == "0%"
    
    def test_generate_report_items_success_rate_error(self, sample_retailer_rules):
        """Test report item generation for success rate below threshold."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            mock_repo.get_success_counters.return_value = (8, 10)  # 80% success rate
            mock_repo.get_progress_at.return_value = (2, None)  # Skip progress rule
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', False)
            items = service._generate_report_items(
                [sample_retailer_rules[0]], date(2024, 1, 1), date(2024, 1, 1)
            )
            
            assert len(items) == 1
            item = items[0]
            assert item.retailer == "Carrefour"
            assert item.status == "error"
            assert item.rule == "success_rate"
            assert item.measured == 0.8
            assert item.threshold == 0.95
            assert "⚠️" in item.message
            assert "80%" in item.message
    
    def test_generate_report_items_success_rate_ok(self, sample_retailer_rules):
        """Test report item generation for success rate above threshold."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            mock_repo.get_success_counters.return_value = (96, 100)  # 96% success rate
            mock_repo.get_progress_at.return_value = (2, None)  # Skip progress rule
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', True)  # Include successes
            items = service._generate_report_items(
                [sample_retailer_rules[0]], date(2024, 1, 1), date(2024, 1, 1)
            )
            
            assert len(items) == 1
            item = items[0]
            assert item.retailer == "Carrefour"
            assert item.status == "success"
            assert item.rule == "success_rate"
            assert item.measured == 0.96
            assert item.threshold == 0.95
            assert "✅" in item.message
            assert "96%" in item.message
    
    def test_generate_report_items_progress_error(self, sample_retailer_rules):
        """Test report item generation for progress below threshold."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            mock_repo.get_success_counters.return_value = (10, 10)  # Perfect success rate
            mock_repo.get_progress_at.return_value = (1, 20)  # 5% progress (below 10% threshold)
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', False)
            items = service._generate_report_items(
                [sample_retailer_rules[0]], date(2024, 1, 1), date(2024, 1, 1)
            )
            
            # Should have both success rate (success) and progress (error) items
            # But since include_successes=False, only error should be included
            error_items = [item for item in items if item.status == "error"]
            assert len(error_items) == 1
            
            progress_item = next(item for item in items if item.rule == "progress_0930")
            assert progress_item.status == "error"
            assert progress_item.measured == 0.05  # 1/20
            assert progress_item.threshold == 0.10
            assert "⚠️" in progress_item.message
            assert "5%" in progress_item.message
    
    def test_generate_report_items_no_data_is_error(self, sample_retailer_rules):
        """Test that zero data counts as an error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            mock_repo.get_success_counters.return_value = (0, 0)  # No data
            mock_repo.get_progress_at.return_value = (0, None)  # Skip progress rule
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', False)
            items = service._generate_report_items(
                [sample_retailer_rules[0]], date(2024, 1, 1), date(2024, 1, 1)
            )
            
            assert len(items) == 1
            item = items[0]
            assert item.status == "error"
            assert item.measured == 0.0
            assert "0%" in item.message
    
    def test_generate_report_items_sorting(self, sample_retailer_rules):
        """Test that report items are sorted correctly (errors first, then by retailer)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            # Setup different results for different retailers
            def mock_success_counters(retailer, date_from, date_to):
                if retailer == "Carrefour":
                    return (8, 10)  # Error: 80% < 95%
                elif retailer == "Intermarché":
                    return (95, 100)  # Success: 95% >= 90%
                else:  # Auchan
                    return (85, 100)  # Error: 85% < 90%
            
            mock_repo.get_success_counters.side_effect = mock_success_counters
            mock_repo.get_progress_at.return_value = (0, None)  # Skip progress rules
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', True)  # Include successes
            items = service._generate_report_items(
                sample_retailer_rules, date(2024, 1, 1), date(2024, 1, 1)
            )
            
            # Should have errors first (Auchan, Carrefour), then successes (Intermarché)
            error_items = [item for item in items if item.status == "error"]
            success_items = [item for item in items if item.status == "success"]
            
            assert len(error_items) == 2
            assert len(success_items) == 1
            
            # Check sorting: errors first, alphabetically
            assert error_items[0].retailer == "Auchan"
            assert error_items[1].retailer == "Carrefour"
            assert success_items[0].retailer == "Intermarché"
    
    def test_csv_generation(self, sample_retailer_rules):
        """Test CSV file generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            mock_repo.get_rules.return_value = sample_retailer_rules[:1]  # Just Carrefour
            mock_repo.get_success_counters.return_value = (8, 10)  # 80% error
            mock_repo.get_progress_at.return_value = (1, 10)  # 10% progress OK
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', False)
            output_path = service.generate_dealer_report(
                date(2024, 1, 1), date(2024, 1, 1), None, "csv"
            )
            
            assert output_path.endswith('.csv')
            assert Path(output_path).exists()
            
            # Check CSV content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'date,retailer,rule,status,measured,threshold' in content
                assert 'Carrefour' in content
                assert 'success_rate' in content
                assert 'error' in content
    
    def test_html_generation(self, sample_retailer_rules):
        """Test HTML file generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_repo = Mock()
            mock_repo.get_rules.return_value = sample_retailer_rules[:1]  # Just Carrefour
            mock_repo.get_success_counters.return_value = (8, 10)  # 80% error
            mock_repo.get_progress_at.return_value = (1, 10)  # 10% progress OK
            
            service = ReportService(mock_repo, temp_dir, 'Europe/Paris', False)
            output_path = service.generate_dealer_report(
                date(2024, 1, 1), date(2024, 1, 1), None, "html"
            )
            
            assert output_path.endswith('.html')
            assert Path(output_path).exists()
            
            # Check HTML content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<!DOCTYPE html>' in content
                assert 'Rapport Dealer' in content
                assert '⚠️ Anomalies' in content
                assert 'Carrefour' in content
                assert '80%' in content
