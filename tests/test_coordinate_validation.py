"""
Tests for coordinate validation in the ETL pipeline.
Ensures coordinates are valid for the Vantaa region.
"""
import pytest
import pandas as pd
from pipeline.etl import SimpleTransformer, SimpleExtractor

@pytest.fixture
def valid_coordinates():
    """Sample of valid Vantaa coordinates"""
    return [
        # Center of Vantaa
        ('24.8474', '60.2934'),
        # Tikkurila
        ('25.0375', '60.2934'),
        # Helsinki-Vantaa Airport
        ('24.9689', '60.3172'),
        # Myyrmäki
        ('24.8527', '60.2613'),
        # Edge cases but still valid
        ('24.7000', '60.2000'),
        ('25.2000', '60.4000'),
    ]

@pytest.fixture
def invalid_coordinates():
    """Sample of invalid coordinates"""
    return [
        # Out of Vantaa bounds
        ('24.5000', '60.2934'),  # Too far west
        ('25.4000', '60.2934'),  # Too far east
        ('24.8474', '60.1000'),  # Too far south
        ('24.8474', '60.5000'),  # Too far north
        # Invalid formats
        ('not-a-number', '60.2934'),
        ('24.8474', 'not-a-number'),
        ('', '60.2934'),
        ('24.8474', ''),
        (None, '60.2934'),
        ('24.8474', None),
    ]

@pytest.fixture
def transformer():
    """Create a SimpleTransformer instance with coordinate validation"""
    class TestTransformer(SimpleTransformer):
        def validate_coordinate(self, lon: str, lat: str) -> bool:
            """Validate a single coordinate pair"""
            try:
                if pd.isna(lon) or pd.isna(lat):
                    return False
                    
                lon_float = float(lon)
                lat_float = float(lat)
                
                # Vantaa bounding box
                VANTAA_BOUNDS = {
                    'lon_min': 24.7,
                    'lon_max': 25.2,
                    'lat_min': 60.2,
                    'lat_max': 60.4
                }
                
                return (VANTAA_BOUNDS['lon_min'] <= lon_float <= VANTAA_BOUNDS['lon_max'] and
                        VANTAA_BOUNDS['lat_min'] <= lat_float <= VANTAA_BOUNDS['lat_max'])
            except (ValueError, TypeError):
                return False

        def validate_coordinates(self, df: pd.DataFrame) -> None:
            """Validate all coordinates in the DataFrame"""
            valid = df.apply(lambda row: self.validate_coordinate(row['x'], row['y']), axis=1)
            if not valid.all():
                invalid_rows = df[~valid]
                raise ValueError(f"Invalid coordinates found: {invalid_rows[['x', 'y']].to_dict('records')}")

    return TestTransformer()

class TestCoordinateValidation:
    """Test suite for coordinate validation functionality"""

    def test_valid_coordinates(self, transformer, valid_coordinates):
        """Test that valid coordinates pass validation"""
        for lon, lat in valid_coordinates:
            df = pd.DataFrame({
                'id': ['1'],
                'ammattiala': ['IT'],
                'tyotehtava': ['Developer'],
                'tyoavain': ['key123'],
                'osoite': ['Test Street 1'],
                'haku_paattyy_pvm': ['2025-12-31'],
                'x': [lon],
                'y': [lat],
                'linkki': ['http://example.com']
            })
            try:
                transformer.validate_coordinates(df)
            except ValueError as e:
                pytest.fail(f"Valid coordinates ({lon}, {lat}) failed validation: {str(e)}")

    def test_invalid_coordinates(self, transformer, invalid_coordinates):
        """Test that invalid coordinates fail validation"""
        for lon, lat in invalid_coordinates:
            df = pd.DataFrame({
                'id': ['1'],
                'ammattiala': ['IT'],
                'tyotehtava': ['Developer'],
                'tyoavain': ['key123'],
                'osoite': ['Test Street 1'],
                'haku_paattyy_pvm': ['2025-12-31'],
                'x': [lon],
                'y': [lat],
                'linkki': ['http://example.com']
            })
            with pytest.raises(ValueError, match="Invalid coordinates found"):
                transformer.validate_coordinates(df)

    def test_mixed_coordinates(self, transformer, valid_coordinates, invalid_coordinates):
        """Test validation with mixed valid and invalid coordinates"""
        df = pd.DataFrame({
            'id': range(len(valid_coordinates) + len(invalid_coordinates)),
            'ammattiala': ['IT'] * (len(valid_coordinates) + len(invalid_coordinates)),
            'tyotehtava': ['Developer'] * (len(valid_coordinates) + len(invalid_coordinates)),
            'tyoavain': ['key123'] * (len(valid_coordinates) + len(invalid_coordinates)),
            'osoite': ['Test Street 1'] * (len(valid_coordinates) + len(invalid_coordinates)),
            'haku_paattyy_pvm': ['2025-12-31'] * (len(valid_coordinates) + len(invalid_coordinates)),
            'x': [x for x, _ in valid_coordinates + invalid_coordinates],
            'y': [y for _, y in valid_coordinates + invalid_coordinates],
            'linkki': ['http://example.com'] * (len(valid_coordinates) + len(invalid_coordinates))
        })
        with pytest.raises(ValueError, match="Invalid coordinates found"):
            transformer.validate_coordinates(df)

    def test_real_api_coordinates(self, transformer, capsys):
        """Test validation with real coordinates from the API"""
        extractor = SimpleExtractor()
        df = extractor()
        
        # Print some statistics about the coordinates
        with capsys.disabled():
            print("\nCoordinate Statistics:")
            print(f"Total records: {len(df)}")
            print("\nLongitude (x) range:")
            print(f"Min: {df['x'].min()}")
            print(f"Max: {df['x'].max()}")
            print("\nLatitude (y) range:")
            print(f"Min: {df['y'].min()}")
            print(f"Max: {df['y'].max()}")
        
        try:
            transformer.validate_coordinates(df)
        except ValueError as e:
            # If validation fails, print the invalid coordinates
            with capsys.disabled():
                print("\nInvalid coordinates found:")
                print(str(e))
            raise
