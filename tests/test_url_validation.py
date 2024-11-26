"""
Tests for URL validation patterns in the ETL pipeline.
"""
import pytest
import pandas as pd
from pipeline.etl import SimpleTransformer

@pytest.fixture
def valid_urls():
    """Sample of valid URLs"""
    return [
        'http://example.com',
        'https://test.com',
        'http://sub.domain.com/path',
        'https://domain.com/path?param=value',
        'http://domain.com/path-with-dash',
        'https://domain.com/path.with.dots',
        'http://domain.com/path_with_underscore',
    ]

@pytest.fixture
def invalid_urls():
    """Sample of invalid URLs"""
    return [
        'not-a-url',
        'ftp://invalid-protocol.com',
        'http:/missing-slash.com',
        'http:///too-many-slashes.com',
        '',
        None
    ]

@pytest.fixture
def transformer():
    """Create a SimpleTransformer instance with URL validation"""
    class TestTransformer(SimpleTransformer):
        def validate_url(self, url: str) -> bool:
            """Validate a single URL"""
            if pd.isna(url):
                return False
            url_pattern = r'^https?://(?:[\w\-]+\.)+[\w\-]+(?:/[\w\-\./\?%&=]*)?$'
            return bool(pd.Series([url]).str.match(url_pattern).iloc[0])

        def validate_urls(self, df: pd.DataFrame) -> None:
            """Validate all URLs in the DataFrame"""
            if not df['linkki'].apply(self.validate_url).all():
                raise ValueError("Invalid URL format")

    return TestTransformer()

class TestURLValidation:
    """Test suite for URL validation functionality"""

    def test_valid_urls(self, transformer, valid_urls):
        """Test that valid URLs pass validation"""
        for url in valid_urls:
            df = pd.DataFrame({
                'id': ['1'],
                'ammattiala': ['IT'],
                'tyotehtava': ['Developer'],
                'tyoavain': ['key123'],
                'osoite': ['Test Street 1'],
                'haku_paattyy_pvm': ['2025-12-31'],
                'x': ['24.123'],
                'y': ['60.123'],
                'linkki': [url]
            })
            try:
                transformer.validate_urls(df)
            except ValueError as e:
                pytest.fail(f"Valid URL {url} failed validation: {str(e)}")

    def test_invalid_urls(self, transformer, invalid_urls):
        """Test that invalid URLs fail validation"""
        for url in invalid_urls:
            df = pd.DataFrame({
                'id': ['1'],
                'ammattiala': ['IT'],
                'tyotehtava': ['Developer'],
                'tyoavain': ['key123'],
                'osoite': ['Test Street 1'],
                'haku_paattyy_pvm': ['2025-12-31'],
                'x': ['24.123'],
                'y': ['60.123'],
                'linkki': [url]
            })
            with pytest.raises(ValueError, match="Invalid URL format"):
                transformer.validate_urls(df)

    def test_mixed_urls(self, transformer, valid_urls, invalid_urls):
        """Test validation with mixed valid and invalid URLs"""
        df = pd.DataFrame({
            'id': range(len(valid_urls) + len(invalid_urls)),
            'ammattiala': ['IT'] * (len(valid_urls) + len(invalid_urls)),
            'tyotehtava': ['Developer'] * (len(valid_urls) + len(invalid_urls)),
            'tyoavain': ['key123'] * (len(valid_urls) + len(invalid_urls)),
            'osoite': ['Test Street 1'] * (len(valid_urls) + len(invalid_urls)),
            'haku_paattyy_pvm': ['2025-12-31'] * (len(valid_urls) + len(invalid_urls)),
            'x': ['24.123'] * (len(valid_urls) + len(invalid_urls)),
            'y': ['60.123'] * (len(valid_urls) + len(invalid_urls)),
            'linkki': valid_urls + invalid_urls
        })
        with pytest.raises(ValueError, match="Invalid URL format"):
            transformer.validate_urls(df)
