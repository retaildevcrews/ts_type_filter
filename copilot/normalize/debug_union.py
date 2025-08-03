"""
Debug the Union behavior issue.
"""

import sys
import os

# Add the parent directory to sys.path to import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import create_normalizer_spec
from ts_type_filter.filter import Define, Struct, Union, Literal, Type


def test_union_behavior():
    """Test that Union works correctly in a simple case."""
    
    type_defs = [
        Define("TestType", [], Struct({
            "name": Union(Literal("a"), Literal("b")),
            "field1?": Literal(0),
        })),
    ]
    
    result = create_normalizer_spec(type_defs)
    name_to_type = result["types"]
    type_to_defaults = result["defaults"]
    
    print("Union test result:")
    print(f"  name_to_type: {name_to_type}")
    print(f"  type_to_defaults: {type_to_defaults}")
    
    # This should work with the current implementation
    expected_name_to_type = {"a": "TestType", "b": "TestType"}
    expected_type_to_defaults = {"TestType": {"field1": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    
    print("Union test passed!")


if __name__ == "__main__":
    test_union_behavior()
