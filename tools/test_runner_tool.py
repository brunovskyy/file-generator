#!/usr/bin/env python3
"""
Test runner for the Document Creator Toolkit.

This script runs all tests and provides detailed reporting.
Supports different test types and output formats.
"""

import sys
import unittest
import os
import time
from pathlib import Path
from io import StringIO

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
from tests.test_data_source_json import TestSourceToJson, TestIntegrationSourceToJson
from tests.test_export_markdown import TestMarkdownExport, TestMarkdownExportIntegration
from tests.test_integration_e2e import TestEndToEndWorkflow, TestCLIIntegration


class TestResult:
    """Store test results for reporting."""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.success_count = 0
        self.start_time = None
        self.end_time = None
    
    def add_success(self, test):
        """Add a successful test."""
        self.success_count += 1
    
    def add_failure(self, test, traceback):
        """Add a failed test."""
        self.failures.append((test, traceback))
    
    def add_error(self, test, traceback):
        """Add an error test."""
        self.errors.append((test, traceback))
    
    def add_skip(self, test, reason):
        """Add a skipped test."""
        self.skipped.append((test, reason))
    
    @property
    def was_successful(self):
        """Check if all tests passed."""
        return len(self.failures) == 0 and len(self.errors) == 0
    
    @property
    def duration(self):
        """Get test duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0


def run_test_suite(test_class, suite_name):
    """Run a specific test suite and return results."""
    print(f"\n{'='*50}")
    print(f"Running {suite_name}")
    print(f"{'='*50}")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    
    # Run tests with custom result handler
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print results
    output = stream.getvalue()
    print(output)
    
    # Summary
    duration = end_time - start_time
    print(f"\n{suite_name} Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    print(f"  Duration: {duration:.2f} seconds")
    
    if result.failures:
        print(f"\n❌ Failures in {suite_name}:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 Errors in {suite_name}:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result


def run_all_tests():
    """Run all test suites."""
    print("🧪 Document Creator Toolkit - Test Suite")
    print("="*60)
    
    # Test suites to run
    test_suites = [
        (TestSourceToJson, "Unit Tests - Source to JSON"),
        (TestIntegrationSourceToJson, "Integration Tests - Source to JSON"),
        (TestMarkdownExport, "Unit Tests - Markdown Export"),
        (TestMarkdownExportIntegration, "Integration Tests - Markdown Export"),
        (TestEndToEndWorkflow, "End-to-End Tests - Complete Workflows"),
        (TestCLIIntegration, "Integration Tests - CLI")
    ]
    
    all_results = []
    total_start_time = time.time()
    
    # Run each test suite
    for test_class, suite_name in test_suites:
        try:
            result = run_test_suite(test_class, suite_name)
            all_results.append((suite_name, result))
        except Exception as e:
            print(f"❌ Failed to run {suite_name}: {e}")
            continue
    
    total_end_time = time.time()
    
    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = 0
    total_successes = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    
    for suite_name, result in all_results:
        total_tests += result.testsRun
        total_successes += result.testsRun - len(result.failures) - len(result.errors)
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        total_skipped += len(result.skipped)
        
        status = "✅" if result.wasSuccessful() else "❌"
        print(f"{status} {suite_name}: {result.testsRun} tests")
    
    print(f"\nTotal Results:")
    print(f"  Tests run: {total_tests}")
    print(f"  Successes: {total_successes}")
    print(f"  Failures: {total_failures}")
    print(f"  Errors: {total_errors}")
    print(f"  Skipped: {total_skipped}")
    print(f"  Duration: {total_end_time - total_start_time:.2f} seconds")
    
    # Success rate
    if total_tests > 0:
        success_rate = (total_successes / total_tests) * 100
        print(f"  Success rate: {success_rate:.1f}%")
    
    # Final status
    if total_failures == 0 and total_errors == 0:
        print(f"\n🎉 All tests passed!")
        return True
    else:
        print(f"\n❌ Some tests failed or had errors")
        return False


def run_specific_test(test_name):
    """Run a specific test or test class."""
    print(f"🧪 Running specific test: {test_name}")
    
    # Map test names to classes
    test_map = {
        "source": TestSourceToJson,
        "source_integration": TestIntegrationSourceToJson,
        "markdown": TestMarkdownExport,
        "markdown_integration": TestMarkdownExportIntegration,
        "e2e": TestEndToEndWorkflow,
        "cli": TestCLIIntegration
    }
    
    if test_name in test_map:
        test_class = test_map[test_name]
        result = run_test_suite(test_class, f"Specific Test - {test_name}")
        return result.wasSuccessful()
    else:
        print(f"❌ Unknown test: {test_name}")
        print(f"Available tests: {list(test_map.keys())}")
        return False


def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    # Check core dependencies
    try:
        import requests
        print("✅ requests - available")
    except ImportError:
        missing_deps.append("requests")
        print("❌ requests - missing")
    
    # Check optional dependencies
    try:
        import yaml
        print("✅ PyYAML - available")
    except ImportError:
        print("⚠️  PyYAML - missing (YAML front matter will use JSON format)")
    
    try:
        import reportlab
        print("✅ reportlab - available")
    except ImportError:
        print("⚠️  reportlab - missing (PDF export will not work)")
    
    try:
        import docx
        print("✅ python-docx - available")
    except ImportError:
        print("⚠️  python-docx - missing (Word export will not work)")
    
    if missing_deps:
        print(f"\n❌ Missing core dependencies: {missing_deps}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    print("\n✅ All core dependencies are available")
    return True


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test runner for Document Creator Toolkit")
    parser.add_argument('--test', '-t', help='Run specific test suite')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Check dependencies first
    if args.check_deps:
        check_dependencies()
        return
    
    if not check_dependencies():
        print("❌ Cannot run tests without core dependencies")
        sys.exit(1)
    
    # Run specific test or all tests
    if args.test:
        success = run_specific_test(args.test)
    else:
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
