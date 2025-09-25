"""Repository for incident and retailer rule data access."""
import logging
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List, Optional, Tuple
import pymysql

logger = logging.getLogger(__name__)


@dataclass
class RetailerRule:
    """Retailer rule configuration."""
    retailer: str
    min_success_rate: Optional[float]
    min_progress_0930: Optional[float]
    include_successes: bool


class IncidentRepository:
    """Repository for accessing incident and retailer rule data."""
    
    def __init__(self, connection: pymysql.Connection):
        """Initialize with database connection.
        
        Args:
            connection: PyMySQL connection object
        """
        self.connection = connection
        
    def get_rules(self, retailer_filter: Optional[str] = None) -> List[RetailerRule]:
        """Get retailer rules, optionally filtered by retailer name.
        
        Args:
            retailer_filter: Optional retailer name to filter by
            
        Returns:
            List of RetailerRule objects
        """
        try:
            with self.connection.cursor() as cursor:
                if retailer_filter:
                    sql = """
                        SELECT retailer, min_success_rate, min_progress_0930, include_successes
                        FROM retailer_rules 
                        WHERE retailer = %s
                    """
                    cursor.execute(sql, (retailer_filter,))
                else:
                    sql = """
                        SELECT retailer, min_success_rate, min_progress_0930, include_successes
                        FROM retailer_rules
                        ORDER BY retailer
                    """
                    cursor.execute(sql)
                
                results = cursor.fetchall()
                return [
                    RetailerRule(
                        retailer=row['retailer'],
                        min_success_rate=row['min_success_rate'],
                        min_progress_0930=row['min_progress_0930'],
                        include_successes=bool(row['include_successes'])
                    )
                    for row in results
                ]
        except pymysql.Error as e:
            logger.error(f"Failed to get retailer rules: {e}")
            return []
    
    def get_success_counters(self, retailer: str, date_from: date, date_to: date) -> Tuple[int, int]:
        """Get success and total counts for a retailer in a date range.
        
        Args:
            retailer: Retailer name
            date_from: Start date (inclusive)
            date_to: End date (inclusive)
            
        Returns:
            Tuple of (success_count, total_count)
        """
        try:
            with self.connection.cursor() as cursor:
                sql = """
                    SELECT 
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                        COUNT(*) as total_count
                    FROM crawler_runs 
                    WHERE retailer = %s 
                    AND planned_for >= %s 
                    AND planned_for <= %s
                """
                cursor.execute(sql, (retailer, date_from, date_to))
                result = cursor.fetchone()
                
                if result:
                    return (
                        int(result['success_count'] or 0),
                        int(result['total_count'] or 0)
                    )
                return (0, 0)
        except pymysql.Error as e:
            logger.error(f"Failed to get success counters for {retailer}: {e}")
            return (0, 0)
    
    def get_progress_at(self, retailer: str, the_date: date, at_time: time) -> Tuple[int, Optional[int]]:
        """Get progress counts for a retailer at a specific time on a date.
        
        Args:
            retailer: Retailer name
            the_date: The date to check
            at_time: The time to check (e.g., 09:30)
            
        Returns:
            Tuple of (completed_by_time, expected_total)
            expected_total is None if it cannot be determined
        """
        try:
            with self.connection.cursor() as cursor:
                # First, try to get expected total from runs_plan
                plan_sql = """
                    SELECT expected_total 
                    FROM runs_plan 
                    WHERE plan_date = %s AND retailer = %s
                """
                cursor.execute(plan_sql, (the_date, retailer))
                plan_result = cursor.fetchone()
                
                expected_total = None
                if plan_result:
                    expected_total = int(plan_result['expected_total'])
                else:
                    # Fallback: count all runs for the day
                    fallback_sql = """
                        SELECT COUNT(*) as total_count
                        FROM crawler_runs 
                        WHERE retailer = %s AND planned_for = %s
                    """
                    cursor.execute(fallback_sql, (retailer, the_date))
                    fallback_result = cursor.fetchone()
                    if fallback_result and fallback_result['total_count'] > 0:
                        expected_total = int(fallback_result['total_count'])
                
                # Count completed runs by the specified time
                completed_sql = """
                    SELECT COUNT(*) as completed_count
                    FROM crawler_runs 
                    WHERE retailer = %s 
                    AND planned_for = %s
                    AND (
                        (finished_at IS NOT NULL AND TIME(finished_at) <= %s)
                        OR 
                        (status IN ('success', 'error') AND TIME(started_at) <= %s)
                    )
                """
                cursor.execute(completed_sql, (retailer, the_date, at_time, at_time))
                completed_result = cursor.fetchone()
                
                completed_by_time = int(completed_result['completed_count'] or 0) if completed_result else 0
                
                return (completed_by_time, expected_total)
                
        except pymysql.Error as e:
            logger.error(f"Failed to get progress for {retailer} at {at_time}: {e}")
            return (0, None)
