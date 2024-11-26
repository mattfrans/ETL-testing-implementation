# ETL Pipeline Testing Documentation

## Overview
This document outlines the testing strategy for the Vantaa job applications ETL (Extract-Transform-Load) pipeline. The pipeline fetches open job applications from the city of Vantaa's API and loads them into a SQLite database.

## Current Project Structure
```
test-case-preliminary-task/
├── pipeline/              # Main ETL code
│   ├── __init__.py
│   ├── const.py          # Constants and configurations
│   ├── etl.py           # Core ETL logic
│   ├── models.py        # Database models
│   └── utils.py         # Utility functions
├── Dockerfile           # Docker configuration
├── requirements.txt     # Project dependencies
└── main.py             # Main entry point
```

## Testing Strategy

### 1. Test Environment Setup
- SQLite3 for local testing
- Python environment with required dependencies

### 2. Testing Dependencies
```
pytest==7.4.3           # Testing framework
pytest-mock==3.12.0     # Mocking functionality
requests-mock==1.11.0   # HTTP request mocking
```

### 3. Testing Layers

#### a. Unit Tests (`test_unit.py`)
- Test individual components in isolation
- Focus on component-specific functionality
- Example: Testing that `SimpleExtractor` correctly initializes with default URL
- Minimal use of mocks, only when necessary (e.g., HTTP requests)
- Test single units of work (one function/method at a time)

#### b. Mock Tests (`test_mock.py`)
- Test component interactions and dependencies
- Heavy use of mocks to isolate from external systems
- Focus on verifying correct interaction patterns
- Example: Testing that `SimpleLoader` correctly calls SQLAlchemy's bulk_save_objects
- No real database or API calls
- Verify behavior through mock assertions

#### c. Integration Tests (`test_integration.py`)
- Test complete workflows and data pipelines
- Use real database connections
- Verify data transformations and persistence
- Handle actual type conversions and constraints
- Example: Testing the full ETL pipeline from API to database

### 4. Key Differences

1. **Unit vs Mock Tests**
   - Unit tests focus on component behavior
   - Mock tests focus on component interactions
   - Unit tests may use some mocks when needed
   - Mock tests use mocks extensively to verify interaction patterns

2. **Mock vs Integration Tests**
   - Mock tests verify correct use of dependencies
   - Integration tests verify actual data flow
   - Mock tests don't hit external systems
   - Integration tests use real databases/APIs

3. **Test Data Handling**
   - Unit tests: Simple, focused test data
   - Mock tests: Test data that exercises interactions
   - Integration tests: Realistic, complete test data

### 5. Current Implementation Coverage

#### a. Extractor Component
- Unit tests: API URL configuration, response parsing
- Mock tests: API interaction patterns
- Integration tests: Real data extraction

#### b. Transformer Component
- Unit tests: Column renaming, date conversion
- Mock tests: Data transformation patterns
- Integration tests: End-to-end data transformation

#### c. Loader Component
- Unit tests: Database connection handling
- Mock tests: SQLAlchemy interaction patterns
- Integration tests: Actual data persistence

### 6. Known Issues
- Data type mismatch between API and database model:
  - API returns integer IDs (e.g., `1`)
  - Database model expects string IDs (Column type: `String`)
  - No automatic type conversion implemented
  - This is caught by integration tests, showing the value of multi-layer testing

### 7. Running Tests

```bash
# Initialize database
python main.py --method init

# Run tests
pytest -v
```

## Case Study: ID Type Mismatch Discovery

This case study demonstrates how our multi-layer testing approach helped identify and understand a data type mismatch issue:

### Issue Discovery Path

1. **Mock Tests Revealed the Issue**
   - Mock test `test_successful_load` in `test_mock.py` failed
   - Initially thought it was a database constraint issue
   - After proper mocking, revealed the real problem: type mismatch between API and model

2. **Testing Layer Contributions**
   - **Unit Tests**: Verified individual component behavior
   - **Mock Tests**: Revealed the type mismatch by testing component interactions
   - **Integration Tests**: Confirmed the issue in a real database context

3. **Key Insights**
   - API returns integer IDs (e.g., `1`)
   - Database model expects string IDs (`Column(String)`)
   - No automatic type conversion in place
   - Mock tests were crucial in isolating and identifying this issue

4. **Resolution Options**
   a. Add type conversion in the loader (recommended)
   b. Change model to accept integers
   c. Transform data at the API boundary

### Testing Strategy Effectiveness

1. **Mock Test Value**
   - Helped isolate the issue from database complexities
   - Revealed component interaction assumptions
   - Showed exact point of type mismatch

2. **Integration Test Value**
   - Verified the issue affects real data flow
   - Provided context for the error's impact
   - Helped validate potential fixes

3. **Lessons Learned**
   - Importance of proper mocking for isolation
   - Value of multi-layer testing approach
   - Need for explicit type handling between components

This case demonstrates how different testing layers work together to not just find issues, but also understand and document them effectively.

## Current Implementation Limitations

1. **Data Validation**
   - Limited to basic DataFrame operations
   - No input data type conversion between API and database
   - No data type validation
   - No coordinate or URL format validation

2. **Error Handling**
   - Basic HTTP status code checking
   - No specific handling for malformed data
   - Limited database error handling

3. **Test Coverage**
   - Basic functionality testing only
   - Limited edge case coverage
   - No performance or stress testing

4. **Known Issues**
   - Data type mismatch between API and database model:
     - API returns integer IDs (e.g., `1`)
     - Database model expects string IDs (Column type: `String`)
     - No automatic type conversion implemented
     - This causes test failures in data loading tests

## Areas Needing Improvement

1. **Data Validation**
   - Add input data structure verification
   - Implement data type checking
   - Add field format validation (coordinates, URLs, dates)

2. **Error Handling**
   - Enhance API error handling
   - Add data transformation error handling
   - Implement database error recovery

3. **Testing Infrastructure**
   - Add test coverage reporting
   - Implement more edge case tests
   - Add performance testing

## Current Testing Focus
1. Basic functionality verification
2. Simple API interaction testing
3. Basic database operation verification

## Priority Data Quality Tests to Add

### 1. Coordinate Validation
```python
def test_invalid_coordinates():
    """Test handling of invalid coordinates"""
    # Test out of range values
    # Test non-numeric values
    # Test precision handling
```

### 2. URL Validation
```python
def test_url_validation():
    """Test URL field validation"""
    # Test malformed URLs
    # Test invalid schemes
    # Test non-ASCII characters
```

### 3. Field Validation
```python
def test_field_constraints():
    """Test field constraints"""
    # Test max length limits
    # Test required vs optional
    # Test character set restrictions
```

### 4. Business Rules
```python
def test_business_rules():
    """Test business rule validation"""
    # Test end date > current date
    # Test working hours format
    # Test location constraints
```

### 5. Data Cleansing
```python
def test_data_cleansing():
    """Test data cleansing rules"""
    # Test whitespace normalization
    # Test case normalization
    # Test special character handling
```

These additional tests will help ensure:
1. Data validity (coordinates, URLs)
2. Data consistency (business rules)
3. Data cleanliness (normalization)
4. Error handling (invalid inputs)

The tests should be implemented in order of priority based on business impact and likelihood of issues.

## Recommended Additional Tests

### 1. Data Quality Tests

#### a. Input Data Validation
- [ ] Test handling of missing required fields
- [ ] Test handling of malformed dates
- [ ] Test handling of invalid coordinates (out of range)
- [ ] Test handling of invalid URLs
- [ ] Test handling of special characters in text fields
- [ ] Test handling of extremely long field values

#### b. Data Transformation Tests
- [ ] Test handling of different date formats
- [ ] Test coordinate precision handling
- [ ] Test field truncation rules
- [ ] Test string normalization (spaces, case)
- [ ] Test handling of numeric precision
- [ ] Test handling of different character encodings

#### c. Data Integrity Tests
- [ ] Test duplicate ID handling
- [ ] Test referential integrity
- [ ] Test data consistency across tables
- [ ] Test handling of updates to existing records
- [ ] Test handling of soft deletes
- [ ] Test data versioning if implemented

### 2. Performance Tests

#### a. Load Testing
- [ ] Test with large datasets (100K+ records)
- [ ] Test concurrent API requests
- [ ] Test database write performance
- [ ] Test memory usage under load
- [ ] Test CPU usage patterns
- [ ] Test network bandwidth usage

#### b. Timing Tests
- [ ] Test ETL pipeline completion time
- [ ] Test individual component timing
- [ ] Test database operation timing
- [ ] Test API response timing
- [ ] Test timeout handling
- [ ] Test performance degradation patterns

### 3. Resilience Tests

#### a. Error Recovery
- [ ] Test API failure recovery
- [ ] Test database connection loss recovery
- [ ] Test partial pipeline failure recovery
- [ ] Test data corruption recovery
- [ ] Test network interruption handling
- [ ] Test system crash recovery

#### b. Resource Constraints
- [ ] Test with limited memory
- [ ] Test with slow network
- [ ] Test with high CPU load
- [ ] Test with disk space constraints
- [ ] Test with database connection limits
- [ ] Test with API rate limiting

### 4. Integration Edge Cases

#### a. API Integration
- [ ] Test API version changes
- [ ] Test API schema changes
- [ ] Test API authentication failures
- [ ] Test API throttling
- [ ] Test API response variations
- [ ] Test API endpoint availability

#### b. Database Integration
- [ ] Test database schema migrations
- [ ] Test database version compatibility
- [ ] Test database connection pooling
- [ ] Test database backup during ETL
- [ ] Test database rollback scenarios
- [ ] Test database constraint violations

### 5. Security Tests

#### a. Data Security
- [ ] Test handling of sensitive data
- [ ] Test data encryption in transit
- [ ] Test data encryption at rest
- [ ] Test access control
- [ ] Test audit logging
- [ ] Test data masking

#### b. System Security
- [ ] Test API authentication
- [ ] Test database connection security
- [ ] Test file system permissions
- [ ] Test network security
- [ ] Test dependency vulnerabilities
- [ ] Test secure configuration

### 6. Monitoring Tests

#### a. Logging
- [ ] Test error logging
- [ ] Test performance logging
- [ ] Test audit logging
- [ ] Test log rotation
- [ ] Test log parsing
- [ ] Test log aggregation

#### b. Metrics
- [ ] Test success/failure metrics
- [ ] Test timing metrics
- [ ] Test resource usage metrics
- [ ] Test business metrics
- [ ] Test alert thresholds
- [ ] Test metric persistence

### Implementation Priority

1. **High Priority**
   - Data quality tests (input validation, transformation)
   - Basic performance tests (reasonable load)
   - Critical error recovery tests
   - Essential security tests

2. **Medium Priority**
   - Extended integration tests
   - Comprehensive performance tests
   - Advanced error scenarios
   - Monitoring implementation

3. **Lower Priority**
   - Edge case handling
   - Advanced security scenarios
   - Detailed metrics
   - Optimization tests

This test expansion will significantly improve the robustness and reliability of the ETL pipeline.

Note: This documentation reflects the current state of implementation. Many features mentioned in the original documentation are planned but not yet implemented.
