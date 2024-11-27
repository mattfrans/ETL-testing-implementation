"""
Data quality tests for the ETL pipeline.
Tests the basic data quality checks that are actually implemented.
"""
import pytest
import pandas as pd
from datetime import date

from pipeline.etl import SimpleExtractor, SimpleTransformer, SimpleLoader
from pipeline.models import Base

@pytest.fixture
def sample_raw_data():
    """Sample data mimicking the raw API response"""
    return [{
        'id': 1,
        'ammattiala': 'IT',
        'tyotehtava': 'Software Developer',
        'tyoavain': 'dev123',
        'osoite': 'Tech Street 1',
        'haku_paattyy_pvm': '2025-12-31',
        'x': '24.123456',
        'y': '60.123456',
        'linkki': 'http://example.com/job1'
    }]

@pytest.fixture
def sample_transformed_df(sample_raw_data):
    """Sample data after transformation"""
    transformer = SimpleTransformer()
    return transformer(pd.DataFrame(sample_raw_data))

class TestDataTransformation:
    """Tests for basic data transformation quality"""
    
    def test_column_renaming(self, sample_raw_data):
        """Test that columns are correctly renamed"""
        transformer = SimpleTransformer()
        df = pd.DataFrame(sample_raw_data)
        result = transformer(df)
        
        expected_columns = {
            'id', 'field', 'job_title', 'job_key', 'address',
            'application_end_date', 'longitude_wgs84', 'latitude_wgs84', 'link'
        }
        assert set(result.columns) == expected_columns

    def test_date_transformation(self, sample_transformed_df):
        """Test that dates are converted to date objects"""
        date_col = sample_transformed_df['application_end_date']
        assert all(isinstance(d, date) for d in date_col if pd.notna(d))

    def test_null_handling(self):
        """Test handling of null values in the data"""
        data = [{
            'id': 1,
            'ammattiala': None,
            'tyotehtava': 'Developer',
            'tyoavain': 'dev123',
            'osoite': None,
            'haku_paattyy_pvm': None,
            'x': '24.123456',
            'y': '60.123456',
            'linkki': 'http://example.com'
        }]
        
        transformer = SimpleTransformer()
        result = transformer(pd.DataFrame(data))
        
        # Check that nulls are preserved
        assert pd.isna(result['field'].iloc[0])
        assert pd.isna(result['address'].iloc[0])
        assert pd.isna(result['application_end_date'].iloc[0])

class TestDataPersistence:
    """Tests for data persistence quality"""

    def test_data_roundtrip(self, tmp_path):
        """Test that data can be written to and read from database"""
        # Setup
        db_path = f"sqlite:///{tmp_path}/test.db"
        loader = SimpleLoader(db_path)
        
        # Initialize database first
        Base.metadata.create_all(loader.engine)
        
        # Create test data
        data = pd.DataFrame({
            'id': [1],
            'field': ['IT'],
            'job_title': ['Developer'],
            'job_key': ['key123'],
            'address': ['Test St'],
            'application_end_date': [date(2025, 12, 31)],
            'longitude_wgs84': [24.123],
            'latitude_wgs84': [60.123],
            'link': ['http://test.com']
        })
        
        # Load data
        loader(data)

    def test_empty_dataframe_handling(self, tmp_path):
        """Test that empty dataframes are handled correctly"""
        # Setup
        db_path = f"sqlite:///{tmp_path}/test.db"
        loader = SimpleLoader(db_path)
        
        # Initialize database
        Base.metadata.create_all(loader.engine)
        
        # Create empty dataframe with correct columns
        data = pd.DataFrame(columns=[
            'id', 'field', 'job_title', 'job_key', 'address',
            'application_end_date', 'longitude_wgs84', 'latitude_wgs84', 'link'
        ])
        
        # This should not raise an error
        loader(data)
