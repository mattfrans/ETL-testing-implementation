"""
Tests for data integrity in the ETL pipeline.
Focuses on core data validation that is actually implemented.
"""
import pytest
import pandas as pd
from datetime import date, datetime, timedelta

from pipeline.etl import SimpleTransformer

class TestDateValidation:
    """Tests for date field validation"""

    def test_valid_future_date(self):
        """Test handling of valid future dates"""
        future_date = (date.today() + timedelta(days=30)).isoformat()
        data = [{
            'id': 1,
            'ammattiala': 'IT',
            'tyotehtava': 'Developer',
            'tyoavain': 'key123',
            'osoite': 'Test St',
            'haku_paattyy_pvm': future_date,
            'x': '24.123456',
            'y': '60.123456',
            'linkki': 'http://example.com'
        }]
        
        transformer = SimpleTransformer()
        result = transformer(pd.DataFrame(data))
        assert isinstance(result['application_end_date'].iloc[0], date)

    def test_malformed_date_handling(self):
        """Test handling of malformed dates"""
        data = [{
            'id': 1,
            'ammattiala': 'IT',
            'tyotehtava': 'Developer',
            'tyoavain': 'key123',
            'osoite': 'Test St',
            'haku_paattyy_pvm': 'not-a-date',
            'x': '24.123456',
            'y': '60.123456',
            'linkki': 'http://example.com'
        }]
        
        transformer = SimpleTransformer()
        with pytest.raises(ValueError):
            transformer(pd.DataFrame(data))

class TestTextFieldValidation:
    """Tests for text field validation"""

    def test_required_fields_presence(self):
        """Test that required fields are present"""
        transformer = SimpleTransformer()
        required_fields = {
            'id', 'field', 'job_title', 'job_key', 'address',
            'application_end_date', 'longitude_wgs84', 'latitude_wgs84', 'link'
        }
        
        data = [{
            'id': 1,
            'ammattiala': 'IT',
            'tyotehtava': 'Developer',
            'tyoavain': 'key123',
            'osoite': 'Test St',
            'haku_paattyy_pvm': '2024-12-31',
            'x': '24.123456',
            'y': '60.123456',
            'linkki': 'http://example.com'
        }]
        
        result = transformer(pd.DataFrame(data))
        assert set(result.columns) == required_fields

    def test_special_characters_handling(self):
        """Test handling of special characters in text fields"""
        data = [{
            'id': 1,
            'ammattiala': 'IT & Software',
            'tyotehtava': 'Developer/Engineer',
            'tyoavain': 'key-123',
            'osoite': 'Test St. #100',
            'haku_paattyy_pvm': '2024-12-31',
            'x': '24.123456',
            'y': '60.123456',
            'linkki': 'http://example.com'
        }]
        
        transformer = SimpleTransformer()
        result = transformer(pd.DataFrame(data))
        
        # Verify special characters are preserved
        assert result['field'].iloc[0] == 'IT & Software'
        assert result['job_title'].iloc[0] == 'Developer/Engineer'
        assert result['job_key'].iloc[0] == 'key-123'
        assert result['address'].iloc[0] == 'Test St. #100'
