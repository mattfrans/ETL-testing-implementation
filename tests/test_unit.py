"""
Unit tests for ETL pipeline components.
Tests the basic functionality of each component in isolation.
"""
import pytest
import pandas as pd
from datetime import date
import requests
from sqlalchemy import create_engine, text

from pipeline.etl import SimpleExtractor, SimpleTransformer, SimpleLoader
from pipeline.models import Base

class TestExtractor:
    """Unit tests for the Extractor component"""

    def test_extractor_initialization(self):
        """Test extractor initialization with default API URL"""
        extractor = SimpleExtractor()
        assert extractor.api_url == "http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki"

    def test_successful_extraction(self, requests_mock):
        """Test basic data extraction from API"""
        test_data = [{
            'id': '1',
            'ammattiala': 'IT',
            'tyotehtava': 'Developer',
            'tyoavain': 'key123',
            'osoite': 'Test St',
            'haku_paattyy_pvm': '2023-12-31',
            'x': '24.123',
            'y': '60.123',
            'linkki': 'http://test.com'
        }]
        
        requests_mock.get(
            "http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki",
            json=test_data
        )
        
        extractor = SimpleExtractor()
        result = extractor()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert list(result.columns) == ['id', 'ammattiala', 'tyotehtava', 'tyoavain', 
                                      'osoite', 'haku_paattyy_pvm', 'x', 'y', 'linkki']

class TestTransformer:
    """Unit tests for the Transformer component"""

    def test_transformer_initialization(self):
        """Test transformer initialization and schema setup"""
        transformer = SimpleTransformer()
        expected_schema = {
            'id': 'id',
            'ammattiala': 'field',
            'tyotehtava': 'job_title',
            'tyoavain': 'job_key',
            'osoite': 'address',
            'haku_paattyy_pvm': 'application_end_date',
            'x': 'longitude_wgs84',
            'y': 'latitude_wgs84',
            'linkki': 'link'
        }
        assert transformer.rename_schema == expected_schema

    def test_column_renaming(self):
        """Test basic column renaming functionality"""
        transformer = SimpleTransformer()
        input_df = pd.DataFrame({
            'id': ['1'],
            'ammattiala': ['IT'],
            'tyotehtava': ['Developer'],
            'tyoavain': ['key123'],
            'osoite': ['Test St'],
            'haku_paattyy_pvm': ['2023-12-31'],
            'x': ['24.123'],
            'y': ['60.123'],
            'linkki': ['http://test.com']
        })
        
        result = transformer._rename_columns(input_df)
        expected_columns = {
            'id', 'field', 'job_title', 'job_key', 'address',
            'application_end_date', 'longitude_wgs84', 'latitude_wgs84', 'link'
        }
        assert set(result.columns) == expected_columns

    def test_date_transformation(self):
        """Test date string to date object conversion"""
        transformer = SimpleTransformer()
        input_df = pd.DataFrame({
            'application_end_date': ['2023-12-31', None, '2024-01-15']
        })
        
        result = transformer._transform_dates(input_df)
        assert isinstance(result['application_end_date'].iloc[0], date)
        assert pd.isna(result['application_end_date'].iloc[1])
        assert isinstance(result['application_end_date'].iloc[2], date)

class TestLoader:
    """Unit tests for the Loader component"""

    def test_loader_initialization(self):
        """Test loader initialization with database connection"""
        loader = SimpleLoader("sqlite:///test.db")
        assert loader.engine is not None

    def test_basic_data_loading(self, tmp_path):
        """Test basic data loading functionality"""
        # Setup
        db_path = f"sqlite:///{tmp_path}/test.db"
        engine = create_engine(db_path)
        Base.metadata.create_all(engine)  # Create tables first
        
        # Create test data
        test_data = pd.DataFrame({
            'id': ['1'],  # Integer ID is converted to string by pipeline
            'field': ['IT'],
            'job_title': ['Developer'],
            'job_key': ['key123'],
            'address': ['Test St'],
            'application_end_date': [date(2023, 12, 31)],
            'longitude_wgs84': [24.123],
            'latitude_wgs84': [60.123],
            'link': ['http://test.com']
        })
        
        # Load data
        loader = SimpleLoader(db_path)
        loader(test_data)
        
        # Verify data was loaded
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM vantaa_open_applications")).fetchone()
            assert result is not None
            assert result.id == '1'  # Compare with string since pipeline converts to string
            assert result.field == 'IT'
            assert result.job_title == 'Developer'
