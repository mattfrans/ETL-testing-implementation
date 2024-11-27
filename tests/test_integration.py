"""
Integration tests for ETL pipeline.
Tests the interaction between components and end-to-end flows.
"""
import pytest
import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text
from pipeline.etl import SimpleExtractor, SimpleTransformer, SimpleLoader, run_etl
from pipeline.models import Base, VantaaOpenApplications
from pipeline.const import TABLE_NAME

@pytest.fixture
def mock_api_response():
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
    }, {
        'id': 2,
        'ammattiala': 'Healthcare',
        'tyotehtava': 'Nurse',
        'tyoavain': 'key456',
        'osoite': 'Hospital Street 456',
        'haku_paattyy_pvm': '2024-06-30',
        'x': '24.456',
        'y': '60.456',
        'linkki': 'http://test2.com'
    }]

@pytest.fixture
def test_db(tmp_path):
    """Create a test database and return its connection string"""
    db_path = f"sqlite:///{tmp_path}/test_integration.db"
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return db_path

class TestETLIntegration:
    def test_extractor_to_transformer(self, requests_mock, mock_api_response):
        """Test data flow from extractor to transformer"""
        # Mock the API response
        requests_mock.get("http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki", json=mock_api_response)
        
        # Extract and transform
        extractor = SimpleExtractor()
        transformer = SimpleTransformer()
        
        extracted_data = extractor()
        transformed_data = transformer(extracted_data)
        
        # Verify the transformation chain
        assert len(transformed_data) == 2
        assert transformed_data['field'].tolist() == ['IT', 'Healthcare']
        assert transformed_data['job_title'].tolist() == ['Python Developer', 'Nurse']
        assert all(isinstance(d, date) for d in transformed_data['application_end_date'] if pd.notna(d))

    def test_transformer_to_loader(self, test_db, mock_api_response):
        """Test data flow from transformer to loader"""
        # Create test data
        df = pd.DataFrame(mock_api_response)
        
        # Transform and load
        transformer = SimpleTransformer()
        loader = SimpleLoader(test_db)
        
        transformed_data = transformer(df)
        loader(transformed_data)
        
        # Verify the data in database
        engine = create_engine(test_db)
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {TABLE_NAME} ORDER BY id"))
            rows = result.fetchall()
            
            assert len(rows) == 2
            assert rows[0].field == 'IT'
            assert rows[1].field == 'Healthcare'
            assert rows[0].job_title == 'Python Developer'
            assert rows[1].job_title == 'Nurse'

    def test_full_pipeline(self, requests_mock, test_db, mock_api_response):
        """Test the entire ETL pipeline end-to-end"""
        # Mock the API response
        requests_mock.get("http://gis.vantaa.fi/rest/tyopaikat/v1/kaikki", json=mock_api_response)
        
        # Run the complete ETL pipeline
        run_etl(test_db)
        
        # Verify the final state in database
        engine = create_engine(test_db)
        with engine.connect() as conn:
            # Check record count
            count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()
            assert count == 2
            
            # Check data integrity
            result = conn.execute(text(f"SELECT * FROM {TABLE_NAME} ORDER BY id"))
            rows = result.fetchall()
            
            # Verify first record
            assert rows[0].field == 'IT'
            assert rows[0].job_title == 'Python Developer'
            assert rows[0].job_key == 'key123'
            assert rows[0].address == 'Test Street 123'
            assert float(rows[0].longitude_wgs84) == 24.123
            assert float(rows[0].latitude_wgs84) == 60.123
            
            # Verify second record
            assert rows[1].field == 'Healthcare'
            assert rows[1].job_title == 'Nurse'
            assert rows[1].job_key == 'key456'
            assert rows[1].address == 'Hospital Street 456'
