"""Database connection factory using PyMySQL."""
import logging
from typing import Any, Dict
import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Factory for creating PyMySQL database connections."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with database configuration.
        
        Args:
            config: Dictionary containing DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
        """
        self.config = config
        
    def create_connection(self) -> pymysql.Connection:
        """Create a new database connection with DictCursor and autocommit.
        
        Returns:
            PyMySQL connection object
            
        Raises:
            pymysql.Error: If connection fails
        """
        try:
            connection = pymysql.connect(
                host=self.config['DB_HOST'],
                port=int(self.config['DB_PORT']),
                user=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'],
                database=self.config['DB_NAME'],
                cursorclass=DictCursor,
                autocommit=True,
                charset='utf8mb4'
            )
            logger.info(f"Connected to database {self.config['DB_NAME']} at {self.config['DB_HOST']}")
            return connection
        except pymysql.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
