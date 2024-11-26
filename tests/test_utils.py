"""
Tests for utility functions in the ETL pipeline.
Tests database initialization and environment reset functionality.
"""
import pytest
import os
from sqlalchemy import create_engine, inspect

from pipeline.utils import initialize_database, reset_enviroment
from pipeline.models import VantaaOpenApplications

class TestDatabaseInitialization:
    """Tests for database initialization functionality"""

    def test_successful_initialization(self, tmp_path):
        """Test successful database initialization"""
        db_path = f"sqlite:///{tmp_path}/test.db"
        
        # Initialize database
        initialize_database(db_path)
        
        # Verify table was created
        engine = create_engine(db_path)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        assert VantaaOpenApplications.__tablename__ in tables
        
        # Verify table structure
        columns = {col['name'] for col in inspector.get_columns(VantaaOpenApplications.__tablename__)}
        expected_columns = {
            'id', 'field', 'job_title', 'job_key', 'address',
            'application_end_date', 'longitude_wgs84', 'latitude_wgs84', 'link'
        }
        assert columns == expected_columns

    def test_reinitialization(self, tmp_path):
        """Test that reinitializing an existing database doesn't raise errors"""
        db_path = f"sqlite:///{tmp_path}/test.db"
        
        # Initialize twice
        initialize_database(db_path)
        initialize_database(db_path)  # Should not raise error
        
        # Verify table still exists
        engine = create_engine(db_path)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert VantaaOpenApplications.__tablename__ in tables

class TestEnvironmentReset:
    """Tests for environment reset functionality"""

    def test_successful_reset(self, tmp_path):
        """Test successful environment reset"""
        # Create a test file
        test_file = tmp_path / "test.db"
        test_file.write_text("test content")
        
        # Verify file exists
        assert os.path.exists(test_file)
        
        # Reset environment
        reset_enviroment(str(test_file))
        
        # Verify file was deleted
        assert not os.path.exists(test_file)

    def test_reset_nonexistent_file(self, tmp_path):
        """Test resetting environment when file doesn't exist"""
        nonexistent_file = tmp_path / "nonexistent.db"
        
        # Verify file doesn't exist
        assert not os.path.exists(nonexistent_file)
        
        # Should not raise error
        reset_enviroment(str(nonexistent_file))

    def test_reset_with_invalid_path(self):
        """Test reset with invalid file path"""
        # Should not raise error with invalid path
        reset_enviroment("")  # Empty path
        reset_enviroment("/invalid/path/that/doesnt/exist")
