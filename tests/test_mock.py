"""
Mock tests for ETL pipeline.
Tests component behavior using mock objects to simulate basic scenarios.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import date
import requests
from sqlalchemy.exc import SQLAlchemyError

from pipeline.etl import SimpleExtractor, SimpleTransformer, SimpleLoader, run_etl, VantaaOpenApplications
from pipeline.models import Base

@pytest.fixture
def mock_api_response():
    """Basic valid API response fixture"""
    return [{
        'id': 1,
        'ammattiala': 'IT',
        'tyotehtava': 'Python Developer',
        'tyoavain': 'key123',
        'osoite': 'Test Street 123',
        'haku_paattyy_pvm': '2023-12-31',
        'x': '24.123',
        'y': '60.123',
        'linkki': 'http://test.com'
    }]

class TestMockExtractor:
    """Tests for Extractor using mocks"""

    def test_successful_api_call(self, requests_mock):
        """Test successful API call with mock response"""
        requests_mock.get(
            "http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki",
            json=[{
                'id': 1,
                'ammattiala': 'IT',
                'tyotehtava': 'Developer',
                'tyoavain': 'key123',
                'osoite': 'Test St',
                'haku_paattyy_pvm': '2023-12-31',
                'x': '24.123',
                'y': '60.123',
                'linkki': 'http://test.com'
            }]
        )
        
        extractor = SimpleExtractor()
        result = extractor()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result['id'].iloc[0] == 1

    def test_http_error_response(self, requests_mock):
        """Test handling of HTTP error response"""
        requests_mock.get(
            "http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki",
            status_code=404
        )
        
        extractor = SimpleExtractor()
        with pytest.raises(requests.exceptions.HTTPError):
            extractor()

class TestMockTransformer:
    """Tests for Transformer using mocks"""

    def test_successful_transformation(self):
        """Test successful data transformation"""
        input_data = pd.DataFrame([{
            'id': 1,
            'ammattiala': 'IT',
            'tyotehtava': 'Developer',
            'tyoavain': 'key123',
            'osoite': 'Test St',
            'haku_paattyy_pvm': '2023-12-31',
            'x': '24.123',
            'y': '60.123',
            'linkki': 'http://test.com'
        }])
        
        transformer = SimpleTransformer()
        result = transformer(input_data)
        
        assert result['field'].iloc[0] == 'IT'
        assert result['job_title'].iloc[0] == 'Developer'
        assert isinstance(result['application_end_date'].iloc[0], date)

class TestMockLoader:
    """Tests for Loader using mocks"""

    @patch('pipeline.etl.create_engine')
    def test_successful_load(self, mock_create_engine):
        """Test successful data loading"""
        # Setup mock engine and session
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_sessionmaker = MagicMock()
        
        # Configure mocks
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = mock_session
        mock_session.__enter__.return_value = mock_session  # For context manager
        
        # Create test data
        data = pd.DataFrame({
            'id': [1],  # Changed to integer
            'field': ['IT'],
            'job_title': ['Developer'],
            'job_key': ['key123'],
            'address': ['Test St'],
            'application_end_date': [date(2023, 12, 31)],
            'longitude_wgs84': [24.123],
            'latitude_wgs84': [60.123],
            'link': ['http://test.com']
        })
        
        # Test loading
        with patch('pipeline.etl.orm.sessionmaker', return_value=mock_sessionmaker):
            # Create and call loader
            loader = SimpleLoader("sqlite:///test.db")
            loader(data)
            
            # Verify the correct methods were called
            assert mock_create_engine.called
            assert mock_session.bulk_save_objects.called
            assert mock_session.commit.called
            
            # Get the objects that were saved
            saved_objects = mock_session.bulk_save_objects.call_args[0][0]
            assert len(saved_objects) == 1
            assert isinstance(saved_objects[0], VantaaOpenApplications)
            assert saved_objects[0].id == 1  # Verify ID remains an integer

class TestMockPipeline:
    """Tests for complete pipeline using mocks"""

    def test_successful_pipeline_run(self, requests_mock, tmp_path):
        """Test successful end-to-end pipeline run with mocks"""
        # Mock API response
        requests_mock.get(
            "http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki",
            json=[{
                'id': 1,  # Integer ID is converted to string by pipeline
                'ammattiala': 'IT',
                'tyotehtava': 'Developer',
                'tyoavain': 'key123',
                'osoite': 'Test St',
                'haku_paattyy_pvm': '2023-12-31',
                'x': '24.123',
                'y': '60.123',
                'linkki': 'http://test.com'
            }]
        )
        
        # Run pipeline
        db_path = f"sqlite:///{tmp_path}/test.db"
        
        # Initialize database first
        from sqlalchemy import create_engine
        engine = create_engine(db_path)
        Base.metadata.create_all(engine)
        
        run_etl(db_path)
        
        # Verify data in database
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM vantaa_open_applications")).fetchone()
            assert result is not None
            assert result.id == 1  # Compare with integer since IDs stay as integers
            assert result.field == 'IT'
