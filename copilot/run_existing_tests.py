"""
Simple test runner for create_defaults tests.
"""

import sys
import os

# Import the test functions directly
sys.path.insert(0, 'tests')
from test_create_defaults import (
    test_basic_example,
    test_type_references,
    test_nested_type_references,
    test_no_optional_fields,
    test_no_name_field,
    test_non_struct_types,
    test_duplicate_names
)


def run_test(test_func, test_name):
    """Run a single test function."""
    try:
        test_func()
        print(f"✓ {test_name} passed")
        return True
    except Exception as e:
        print(f"✗ {test_name} failed: {e}")
        return False


if __name__ == "__main__":
    tests = [
        (test_basic_example, "test_basic_example"),
        (test_type_references, "test_type_references"),
        (test_nested_type_references, "test_nested_type_references"),
        (test_no_optional_fields, "test_no_optional_fields"),
        (test_no_name_field, "test_no_name_field"),
        (test_non_struct_types, "test_non_struct_types"),
        (test_duplicate_names, "test_duplicate_names")
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, test_name in tests:
        if run_test(test_func, test_name):
            passed += 1
    
    print(f"\n{passed}/{total} tests passed")
    if passed == total:
        print("🎉 All existing tests pass!")
    else:
        print("❌ Some tests failed")
