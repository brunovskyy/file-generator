# Testing Framework - Document Creator Toolkit

## 📋 Overview

This testing framework provides comprehensive testing for the Document Creator Toolkit, including **unit tests**, **integration tests**, and **end-to-end tests**. The framework is designed to ensure code quality, reliability, and maintainability.

## 🧪 Types of Tests

### 1. **Unit Tests** ✅
**Definition**: Unit tests test individual functions or methods in isolation, without dependencies on external systems.

**Purpose**: 
- Verify that each function works correctly with various inputs
- Test edge cases and error conditions
- Ensure functions handle invalid inputs gracefully
- Fast execution and easy debugging

**Examples in our project**:
```python
# Testing a single function
def test_detect_source_format_json_file(self):
    """Test detecting JSON file format."""
    self.assertEqual(detect_source_format("data.json"), "json")
    self.assertEqual(detect_source_format("DATA.JSON"), "json")

# Testing error handling
def test_detect_source_format_empty_source(self):
    """Test error handling for empty source."""
    with self.assertRaises(DataSourceError):
        detect_source_format("")
```

### 2. **Integration Tests** ✅
**Definition**: Integration tests verify that different components work together correctly.

**Purpose**:
- Test interactions between modules
- Verify data flows between components
- Test with real files and data
- Ensure components integrate properly

**Examples in our project**:
```python
# Testing data loading with real files
def test_load_normalized_data_json_file(self):
    """Test loading normalized data from JSON file."""
    result = load_normalized_data(self.test_json_file)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0]["name"], "John")
```

### 3. **End-to-End Tests** ✅
**Definition**: End-to-end tests simulate complete user workflows from start to finish.

**Purpose**:
- Test complete user scenarios
- Verify the entire application workflow
- Test with realistic data and conditions
- Ensure the system works as users expect

**Examples in our project**:
```python
# Testing complete workflow: JSON → Markdown
def test_json_to_markdown_workflow(self):
    """Test complete workflow: JSON → Markdown."""
    # Load data
    data = load_normalized_data(self.test_json_file)
    
    # Export to Markdown
    result_files = export_to_markdown(data, self.output_dir)
    
    # Verify results
    self.assertEqual(len(result_files), 3)
```

## 🚀 Quick Start

### Running All Tests
```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose
```

### Running Specific Test Suites
```bash
# Run only unit tests for source loading
python run_tests.py --test source

# Run only Markdown export tests
python run_tests.py --test markdown

# Run only end-to-end tests
python run_tests.py --test e2e
```

### Check Dependencies
```bash
# Check if all testing dependencies are available
python run_tests.py --check-deps
```

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_source_to_json.py      # Unit & integration tests for data loading
├── test_markdown_export.py     # Unit & integration tests for Markdown export
├── test_end_to_end.py         # End-to-end workflow tests
└── README.md                  # This file

run_tests.py                   # Main test runner script
```

## 📊 Test Coverage

### Source to JSON Module (`test_source_to_json.py`)
- ✅ **Unit Tests**: 15 tests
  - Format detection (JSON, CSV, API, URLs)
  - CSV row to nested object conversion
  - Data source validation
  - Error handling for invalid inputs

- ✅ **Integration Tests**: 4 tests
  - Loading real JSON files
  - Loading real CSV files
  - Auto-format detection
  - Error handling with real files

### Markdown Export Module (`test_markdown_export.py`)
- ✅ **Unit Tests**: 12 tests
  - Filename generation and sanitization
  - YAML front matter creation
  - Markdown content generation
  - Key extraction and selection

- ✅ **Integration Tests**: 6 tests
  - Complete Markdown export workflow
  - File creation and content verification
  - YAML front matter integration
  - Error handling scenarios

### End-to-End Tests (`test_end_to_end.py`)
- ✅ **Workflow Tests**: 8 tests
  - Complete JSON → Markdown workflow
  - Complete CSV → Markdown workflow
  - Data validation workflows
  - Edge case handling

- ✅ **CLI Integration**: 2 tests
  - Command-line interface testing
  - Argument processing verification

## 🔧 Test Execution

### Automated Test Runner
The `run_tests.py` script provides:

- **Dependency checking**: Verifies required packages are installed
- **Test suite organization**: Runs tests in logical groups
- **Detailed reporting**: Shows success/failure counts and timing
- **Error reporting**: Provides detailed error messages and tracebacks
- **Exit codes**: Returns appropriate exit codes for CI/CD integration

### Example Test Output
```
🧪 Document Creator Toolkit - Test Suite
============================================================

==================================================
Running Unit Tests - Source to JSON
==================================================

test_detect_source_format_json_file ... ok
test_detect_source_format_csv_file ... ok
test_convert_csv_row_to_nested_object_basic ... ok
...

Unit Tests - Source to JSON Summary:
  Tests run: 15
  Successes: 15
  Failures: 0
  Errors: 0
  Duration: 0.05 seconds

============================================================
OVERALL TEST SUMMARY
============================================================
✅ Unit Tests - Source to JSON: 15 tests
✅ Integration Tests - Source to JSON: 4 tests
✅ Unit Tests - Markdown Export: 12 tests
✅ Integration Tests - Markdown Export: 6 tests
✅ End-to-End Tests - Complete Workflows: 8 tests
✅ Integration Tests - CLI: 2 tests

Total Results:
  Tests run: 47
  Successes: 47
  Failures: 0
  Errors: 0
  Duration: 2.34 seconds
  Success rate: 100.0%

🎉 All tests passed!
```

## 🛠 Writing New Tests

### Unit Test Example
```python
def test_your_function(self):
    """Test your function with specific input."""
    # Arrange
    input_data = {"key": "value"}
    expected_result = "expected_output"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    self.assertEqual(result, expected_result)
```

### Integration Test Example
```python
def test_component_integration(self):
    """Test integration between components."""
    # Set up test data
    test_file = self.create_test_file()
    
    # Test the integration
    data = load_data(test_file)
    result = process_data(data)
    
    # Verify results
    self.assertIsNotNone(result)
    self.assertEqual(len(result), expected_count)
```

### End-to-End Test Example
```python
def test_complete_workflow(self):
    """Test complete user workflow."""
    # Simulate user actions
    source_file = self.create_test_data()
    
    # Run complete workflow
    data = load_normalized_data(source_file)
    files = export_to_markdown(data, self.output_dir)
    
    # Verify end result
    self.assertTrue(all(f.exists() for f in files))
```

## 🔍 Debugging Tests

### Running Single Tests
```bash
# Run a specific test method
python -m unittest tests.test_source_to_json.TestSourceToJson.test_detect_source_format_json_file

# Run a specific test class
python -m unittest tests.test_source_to_json.TestSourceToJson
```

### Debugging Tips
1. **Use descriptive test names**: Tests should clearly describe what they're testing
2. **Add debug prints**: Temporarily add print statements to understand test flow
3. **Check test data**: Verify that test fixtures are created correctly
4. **Use unittest's debug mode**: Run with `-v` flag for verbose output

## 📈 Test Metrics

### Current Test Statistics
- **Total Tests**: 47
- **Unit Tests**: 27 (57%)
- **Integration Tests**: 12 (26%)
- **End-to-End Tests**: 8 (17%)
- **Code Coverage**: High coverage of core functionality
- **Test Execution Time**: ~2-3 seconds for full suite

### Quality Metrics
- ✅ **Error Handling**: All major error conditions tested
- ✅ **Edge Cases**: Boundary conditions and unusual inputs tested
- ✅ **Data Validation**: Input validation thoroughly tested
- ✅ **File Operations**: File creation, reading, and writing tested
- ✅ **User Workflows**: Complete user scenarios tested

## 🚨 Dependency Issues & Solutions

### Missing Dependencies
If you see import errors for optional dependencies:

```bash
# Install missing dependencies
pip install PyYAML reportlab python-docx docxtpl

# Or install all optional dependencies
pip install -r requirements.txt
```

### Dependency-Specific Tests
- **PyYAML**: Tests will fall back to JSON format if PyYAML is not available
- **ReportLab**: PDF export tests will be skipped if ReportLab is not installed
- **python-docx**: Word export tests will be skipped if python-docx is not installed

## 🎯 Best Practices

### Test Organization
1. **Group related tests**: Use test classes to group related functionality
2. **Use descriptive names**: Test names should clearly indicate what is being tested
3. **Follow AAA pattern**: Arrange, Act, Assert in each test
4. **Keep tests independent**: Each test should be able to run in isolation

### Test Data Management
1. **Use fixtures**: Create reusable test data in `setUp()` methods
2. **Clean up**: Always clean up test files and directories in `tearDown()`
3. **Use temporary directories**: Don't create permanent test files
4. **Mock external dependencies**: Use mocks for external services

### Error Testing
1. **Test error conditions**: Always test how functions handle invalid inputs
2. **Use assertRaises**: Verify that expected exceptions are raised
3. **Test error messages**: Ensure error messages are helpful and accurate

## 🔄 Continuous Integration

The test framework is designed to work with CI/CD systems:

```yaml
# Example CI configuration
- name: Run Tests
  run: |
    python run_tests.py
    echo "Exit code: $?"
```

### CI-Friendly Features
- **Exit codes**: Returns 0 for success, 1 for failure
- **Structured output**: Clear reporting for automated parsing
- **Dependency checking**: Verifies environment before running tests
- **Parallel execution**: Tests can be run in parallel if needed

## 📚 Additional Resources

### Python Testing Documentation
- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [Testing in Python](https://docs.python-guide.org/writing/tests/)
- [Best Practices for Testing](https://docs.python-guide.org/writing/tests/#tools)

### Testing Types Explained
- **Unit Testing**: Testing individual components in isolation
- **Integration Testing**: Testing interactions between components
- **End-to-End Testing**: Testing complete user workflows
- **Functional Testing**: Testing specific functionality from user perspective

---

## 🏆 Summary

This testing framework provides:
- **Comprehensive Coverage**: Unit, integration, and end-to-end tests
- **Easy Execution**: Simple commands to run all or specific tests
- **Clear Reporting**: Detailed output with success/failure information
- **Maintainable Structure**: Well-organized test code that's easy to extend
- **CI/CD Ready**: Suitable for automated testing in deployment pipelines

The framework ensures that the Document Creator Toolkit is reliable, maintainable, and works correctly across different scenarios and use cases.
