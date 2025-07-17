#!/usr/bin/env python3
"""
Simplified Test Runner for Document Creator Toolkit
==================================================

This script runs the unified tests that address the organization concerns.
"""

import sys
import os
import unittest
from pathlib import Path

# Add the parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Run the simplified, organized tests."""
    
    print("🧪 Document Creator Toolkit - Simplified Test Suite")
    print("=" * 60)
    
    # Check if test data directory exists
    test_data_dir = Path(__file__).parent / "data"
    if not test_data_dir.exists():
        print("📁 Creating test data directory...")
        test_data_dir.mkdir(exist_ok=True)
    
    # Create test data if it doesn't exist
    _ensure_test_data_exists()
    
    # Discover and run unified tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_unified_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    print(f"✅ Tests run: {total_tests}")
    print(f"✅ Successes: {successes}")
    print(f"❌ Failures: {failures}")
    print(f"💥 Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 All tests passed! Your toolkit is working perfectly!")
        return 0
    else:
        print(f"\n⚠️ Some tests need attention. Success rate: {(successes/total_tests)*100:.1f}%")
        return 1


def _ensure_test_data_exists():
    """Ensure test data files exist."""
    test_data_dir = Path(__file__).parent / "data"
    
    # Create JSON test data
    json_file = test_data_dir / "test_data.json"
    if not json_file.exists():
        print("📝 Creating test JSON data...")
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "profile": {
                    "age": 30,
                    "location": "New York"
                },
                "department": "Engineering",
                "projects": [
                    {"name": "Project A", "status": "completed"},
                    {"name": "Project B", "status": "in-progress"}
                ]
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "profile": {
                    "age": 25,
                    "location": "San Francisco"
                },
                "department": "Design",
                "projects": [
                    {"name": "Project C", "status": "completed"},
                    {"name": "Project D", "status": "planning"}
                ]
            }
        ]
        
        with open(json_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(test_data, f, indent=2)
    
    # Create CSV test data
    csv_file = test_data_dir / "test_data.csv"
    if not csv_file.exists():
        print("📝 Creating test CSV data...")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            
            # CSV headers
            writer.writerow([
                "name", "email", "profile.age", "profile.location", 
                "department", "projects"
            ])
            
            # CSV data
            writer.writerow([
                "John Doe", "john@example.com", "30", "New York", 
                "Engineering", '[{"name": "Project A", "status": "completed"}, {"name": "Project B", "status": "in-progress"}]'
            ])
            writer.writerow([
                "Jane Smith", "jane@example.com", "25", "San Francisco",
                "Design", '[{"name": "Project C", "status": "completed"}, {"name": "Project D", "status": "planning"}]'
            ])


if __name__ == "__main__":
    sys.exit(main())
