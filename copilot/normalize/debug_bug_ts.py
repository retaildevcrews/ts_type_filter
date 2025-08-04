#!/usr/bin/env python3
"""
Debug script to investigate why create_normalizer_spec() isn't working correctly on bug.ts
"""

import sys
import os

# Add the current directory to sys.path so we can import ts_type_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ts_type_filter import parse, create_normalizer_spec


def debug_bug_ts():
    """Debug create_normalizer_spec on the bug.ts file."""
    
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
    
    print("=== DEBUGGING create_normalizer_spec() ===\n")
    
    # Parse the TypeScript content
    print("1. Parsing TypeScript...")
    type_defs = parse(ts_content)
    print(f"   Parsed {len(type_defs)} type definitions:")
    
    for i, type_def in enumerate(type_defs):
        print(f"   {i+1}. {type_def.name}: {type_def}")
        print(f"      Parameters: {type_def.params}")
        print(f"      Type: {type_def.type}")
        print()
    
    # Test create_normalizer_spec
    print("2. Running create_normalizer_spec()...")
    result = create_normalizer_spec(type_defs)
    
    print("\n3. Results Analysis:")
    print(f"   Types mapping: {result['types']}")
    print(f"   Defaults: {result['defaults']}")
    print(f"   Duplicates: {result['duplicates']}")
    
    print("\n4. Expected vs Actual:")
    expected_types = {"a": "GROUP1", "b": "GROUP1", "c": "GROUP2", "d": "GROUP2"}
    expected_defaults = {
        "GROUP1": {"field1": None},  # From OPTION expansion
        "GROUP2": {"field4": None}   # From BOOLEANOPTION expansion (field4 is optional, field3 is required)
    }
    
    print(f"   Expected types: {expected_types}")
    print(f"   Actual types:   {result['types']}")
    print(f"   Types match: {result['types'] == expected_types}")
    print()
    
    print(f"   Expected defaults: {expected_defaults}")
    print(f"   Actual defaults:   {result['defaults']}")
    
    # Detailed comparison
    print("\n5. Detailed Issues:")
    issues = []
    
    # Check GROUP2 missing
    if "GROUP2" not in result['defaults']:
        issues.append("GROUP2 is missing from defaults (should have empty dict {})")
    
    # Check OPTION present
    if "OPTION" in result['defaults']:
        issues.append("OPTION should not be in defaults (it's a generic type definition)")
    
    # Check BOOLEANOPTION present  
    if "BOOLEANOPTION" in result['defaults']:
        issues.append("BOOLEANOPTION should not be in defaults (it's a generic type definition)")
        
    if issues:
        print("   Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("   No issues found!")
        
    print("\n6. Conclusion:")
    if result['types'] == expected_types and result['defaults'] == expected_defaults:
        print("   SUCCESS: Function works correctly")
    else:
        print("   PROBLEM: Function has issues with generic type expansion")
        print("   The bug described in copilot/normalize_spec.md is confirmed")


if __name__ == "__main__":
    debug_bug_ts()
