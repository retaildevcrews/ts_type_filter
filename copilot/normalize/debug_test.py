#!/usr/bin/env python3
"""
Debug version of the test to see detailed output
"""

import sys
import os

# Add the root directory to sys.path so we can import ts_type_filter
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, root_dir)

from ts_type_filter import parse, create_normalizer_spec
import json


def debug_test():
    """Debug version to see what's happening."""
    
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
    
    print("=== PARSING ===")
    type_defs = parse(ts_content)
    print(f"Parsed {len(type_defs)} type definitions:")
    
    for i, type_def in enumerate(type_defs):
        print(f"{i+1}. Type: {type_def.name}")
        print(f"   Class: {type(type_def).__name__}")
        if hasattr(type_def, 'type'):
            print(f"   Type obj: {type(type_def.type).__name__}")
        if hasattr(type_def, 'params'):
            print(f"   Params: {type_def.params}")
        print()
    
    print("=== TESTING create_normalizer_spec ===")
    result = create_normalizer_spec(type_defs)
    
    print("Result structure:")
    print(f"Keys: {list(result.keys())}")
    print()
    
    print("Types mapping:")
    for k, v in result['types'].items():
        print(f"  '{k}' -> '{v}'")
    print()
    
    print("Defaults:")
    for k, v in result['defaults'].items():
        print(f"  '{k}' -> {v}")
    print()
    
    print("Duplicates:")
    print(f"  {result['duplicates']}")
    print()
    
    # Expected results
    expected_types = {"a": "GROUP1", "b": "GROUP1", "c": "GROUP2", "d": "GROUP2"}
    expected_defaults = {
        "GROUP1": {"field1": None},
        "GROUP2": {"field4": None}
    }
    
    print("=== COMPARISON ===")
    print("Expected types:", expected_types)
    print("Actual types:  ", result['types'])
    print("Types match:", result['types'] == expected_types)
    print()
    
    print("Expected defaults:", expected_defaults)
    print("Actual defaults:  ", result['defaults'])
    print("Defaults match:", result['defaults'] == expected_defaults)


if __name__ == "__main__":
    debug_test()
