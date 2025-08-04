#!/usr/bin/env python3
"""
Test script to check if create_normalizer_spec() works on copilot/normalize/bug.ts
"""

import sys
import os

# Add the current directory to sys.path so we can import ts_type_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ts_type_filter import parse, create_normalizer_spec


def test_bug_ts():
    """Test create_normalizer_spec on the bug.ts file."""
    
    # Use the TypeScript content without the comment (which causes parsing issues)
    ts_content = '''type GROUPS = GROUP1 | GROUP2;
type GROUP1 = OPTION<"a" | "b">;
type GROUP2 = BOOLEANOPTION<"c" | "d">;

type OPTION<NAME> = {
  name: NAME;
  field1?: number;
  field2: string;
}

type BOOLEANOPTION<NAME> = {
  name: NAME;
  field3: number;
  field4?: string;
}'''
    
    print("TypeScript content:")
    print("-" * 40)
    print(ts_content)
    print("-" * 40)
    
    # Parse the TypeScript content
    print("\nParsing TypeScript...")
    try:
        type_defs = parse(ts_content)
        print(f"Successfully parsed {len(type_defs)} type definitions")
        
        # Print each type definition
        for i, type_def in enumerate(type_defs):
            print(f"  {i+1}. {type_def}")
        
    except Exception as e:
        print(f"Parse error: {e}")
        return
    
    # Test create_normalizer_spec
    print("\nTesting create_normalizer_spec()...")
    try:
        result = create_normalizer_spec(type_defs)
        
        print("\nResult:")
        print(f"  Types mapping: {result['types']}")
        print(f"  Defaults: {result['defaults']}")
        print(f"  Duplicates: {result['duplicates']}")
        
        # Check if the function handles the generic types correctly
        expected_types = {"a": "GROUP1", "b": "GROUP1", "c": "GROUP2", "d": "GROUP2"}
        expected_defaults = {
            "GROUP1": {"field1": None},
            "GROUP2": {"field4": None}  # field4 is optional, field3 is required
        }
        
        print("\nExpected vs Actual:")
        print(f"  Expected types: {expected_types}")
        print(f"  Actual types:   {result['types']}")
        
        print(f"  Expected defaults: {expected_defaults}")
        print(f"  Actual defaults:   {result['defaults']}")
        
        # Check if results match expectations
        types_match = result['types'] == expected_types
        defaults_match = result['defaults'] == expected_defaults
        # # For defaults, we need to handle the case where some might not be present
        # defaults_match = True
        # for type_name, expected_default in expected_defaults.items():
        #     if type_name not in result['defaults']:
        #         if expected_default:  # Only fail if we expected non-empty defaults
        #             defaults_match = False
        #             break
        #     elif result['defaults'][type_name] != expected_default:
        #         defaults_match = False
        #         break
        
        print(f"\nResults analysis:")
        print(f"  Types match expected: {types_match}")
        print(f"  Defaults match expected: {defaults_match}")
        
        if types_match and defaults_match:
            print("SUCCESS: create_normalizer_spec() works correctly on bug.ts!")
        else:
            print("ISSUE: create_normalizer_spec() doesn't handle the generic types as expected")
            print("   This confirms the bug described in the copilot/normalize_spec.md file")
        
    except Exception as e:
        print(f"Error running create_normalizer_spec: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_bug_ts()
