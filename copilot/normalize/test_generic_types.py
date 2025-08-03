"""
Test file to reproduce and validate the generic type expansion issue.
"""

import sys
import os

# Add the parent directory to sys.path to import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import create_normalizer_spec
from ts_type_filter.filter import Define, Struct, Union, Literal, Type


def test_generic_type_issue():
    """Test that demonstrates the fixed generic type functionality."""
    
    # This represents: type GROUP = OPTION<"a" | "b">;
    # and: type OPTION<NAME> = { name: NAME; field1?: number; field2: string; }
    type_defs = [
        # Generic type definition: OPTION<NAME> = { name: NAME; field1?: number; field2: string; }
        Define("OPTION", ["NAME"], Struct({
            "name": Type("NAME"),  # This is a type parameter
            "field1?": Literal(0),  # optional field with number type
            "field2": Literal(""),  # required field with string type
        })),
        
        # Type that uses the generic: GROUP = OPTION<"a" | "b">
        Define("GROUP", [], Type("OPTION", [Union(Literal("a"), Literal("b"))])),
    ]
    
    result = create_normalizer_spec(type_defs)
    name_to_type = result["types"]
    type_to_defaults = result["defaults"]
    duplicates = result["duplicates"]
    
    print("Fixed result:")
    print(f"  name_to_type: {name_to_type}")
    print(f"  type_to_defaults: {type_to_defaults}")
    print(f"  duplicates: {duplicates}")
    
    # Now GROUP should be processed correctly
    expected_name_to_type = {"a": "GROUP", "b": "GROUP"}
    expected_type_to_defaults = {
        "OPTION": {"field1": None},  # The original OPTION type
        "GROUP": {"field1": None}    # The expanded GROUP type
    }
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"
    
    print("Test passed - generic type expansion works!")


def test_expected_behavior():
    """Test what we want the behavior to be after fixing the issue."""
    
    # After the fix, we want GROUP to be treated as if it were:
    # type GROUP = { name: "a" | "b"; field1?: number; field2: string; }
    expected_type_defs = [
        Define("GROUP", [], Struct({
            "name": Union(Literal("a"), Literal("b")),
            "field1?": Literal(0),  # optional field
            "field2": Literal(""),  # required field
        })),
    ]
    
    result = create_normalizer_spec(expected_type_defs)
    name_to_type = result["types"]
    type_to_defaults = result["defaults"]
    
    print("\nExpected behavior after fix:")
    print(f"  name_to_type: {name_to_type}")
    print(f"  type_to_defaults: {type_to_defaults}")
    
    # This is what we want to achieve
    expected_name_to_type = {"a": "GROUP", "b": "GROUP"}
    expected_type_to_defaults = {"GROUP": {"field1": None}}
    
    print(f"  expected_name_to_type: {expected_name_to_type}")
    print(f"  expected_type_to_defaults: {expected_type_to_defaults}")
    
    assert name_to_type == expected_name_to_type
    assert type_to_defaults == expected_type_to_defaults
    
    print("Expected behavior test passed")


if __name__ == "__main__":
    test_generic_type_issue()
    test_expected_behavior()
    print("\nAll tests passed!")
