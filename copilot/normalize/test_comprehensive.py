"""
Comprehensive test for the generic type expansion functionality.
Tests various edge cases and scenarios.
"""

import sys
import os

# Add the parent directory to sys.path to import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import create_normalizer_spec
from ts_type_filter.filter import Define, Struct, Union, Literal, Type


def test_basic_generic_expansion():
    """Test basic generic type expansion."""
    
    type_defs = [
        Define("Option", ["T"], Struct({
            "name": Type("T"),
            "value?": Literal(None),
        })),
        Define("StringOption", [], Type("Option", [Literal("string_choice")])),
    ]
    
    result = create_normalizer_spec(type_defs)
    
    expected_name_to_type = {"string_choice": "StringOption"}
    expected_type_to_defaults = {
        "Option": {"value": None},
        "StringOption": {"value": None}
    }
    
    assert result["types"] == expected_name_to_type
    assert result["defaults"] == expected_type_to_defaults
    assert not result["duplicates"]
    
    print("✓ Basic generic expansion test passed")


def test_multiple_type_parameters():
    """Test generic with multiple type parameters."""
    
    type_defs = [
        Define("Choice", ["NAME", "VALUE"], Struct({
            "name": Type("NAME"),
            "value": Type("VALUE"),
            "optional?": Literal(True),
        })),
        Define("ColorChoice", [], Type("Choice", [
            Union(Literal("red"), Literal("blue")),
            Literal("#color")
        ])),
    ]
    
    result = create_normalizer_spec(type_defs)
    
    expected_name_to_type = {"red": "ColorChoice", "blue": "ColorChoice"}
    expected_type_to_defaults = {
        "Choice": {"optional": None},
        "ColorChoice": {"optional": None}
    }
    
    assert result["types"] == expected_name_to_type
    assert result["defaults"] == expected_type_to_defaults
    
    print("✓ Multiple type parameters test passed")


def test_nested_generic_references():
    """Test nested type references (not currently supported, should be ignored)."""
    
    type_defs = [
        Define("Wrapper", ["T"], Struct({
            "content": Type("T"),
        })),
        Define("Option", ["NAME"], Struct({
            "name": Type("NAME"),
            "active?": Literal(False),
        })),
        Define("WrappedOption", [], Type("Wrapper", [Type("Option", [Literal("wrapped")])])),
    ]
    
    result = create_normalizer_spec(type_defs)
    
    # WrappedOption should not be processed since it doesn't directly resolve to a struct with name field
    expected_name_to_type = {}
    expected_type_to_defaults = {
        "Option": {"active": None}
    }
    
    assert result["types"] == expected_name_to_type
    assert result["defaults"] == expected_type_to_defaults
    
    print("✓ Nested generic references test passed")


def test_non_struct_generic():
    """Test generic that doesn't resolve to a struct (should be ignored)."""
    
    type_defs = [
        Define("Identity", ["T"], Type("T")),
        Define("MyString", [], Type("Identity", [Literal("test")])),
    ]
    
    result = create_normalizer_spec(type_defs)
    
    # Should be empty since Identity doesn't resolve to a struct
    assert result["types"] == {}
    assert result["defaults"] == {}
    assert not result["duplicates"]
    
    print("✓ Non-struct generic test passed")


def test_circular_reference():
    """Test circular references (should be handled gracefully)."""
    
    type_defs = [
        Define("Node", ["T"], Struct({
            "name": Type("T"),
            "next": Type("Node", [Type("T")]),
            "data?": Literal(None),
        })),
        Define("StringNode", [], Type("Node", [Literal("node")])),
    ]
    
    result = create_normalizer_spec(type_defs)
    
    expected_name_to_type = {"node": "StringNode"}
    expected_type_to_defaults = {
        "Node": {"data": None},
        "StringNode": {"data": None}
    }
    
    assert result["types"] == expected_name_to_type
    assert result["defaults"] == expected_type_to_defaults
    
    print("✓ Circular reference test passed")


def test_wrong_parameter_count():
    """Test generic called with wrong number of parameters (should be ignored)."""
    
    type_defs = [
        Define("Pair", ["A", "B"], Struct({
            "name": Type("A"),
            "second": Type("B"),
        })),
        Define("WrongCall", [], Type("Pair", [Literal("only_one")])),  # Should have 2 params
    ]
    
    result = create_normalizer_spec(type_defs)
    
    # WrongCall should be ignored due to parameter count mismatch
    assert result["types"] == {}
    assert result["defaults"] == {}
    
    print("✓ Wrong parameter count test passed")


def test_original_functionality_preserved():
    """Test that original non-generic functionality still works."""
    
    type_defs = [
        Define("Direct", [], Struct({
            "name": Union(Literal("x"), Literal("y")),
            "field?": Literal(42),
        })),
        Define("Generic", ["T"], Struct({
            "name": Type("T"),
            "generic?": Literal("gen"),
        })),
        Define("Applied", [], Type("Generic", [Literal("applied")])),
    ]
    
    result = create_normalizer_spec(type_defs)
    
    expected_name_to_type = {
        "x": "Direct", 
        "y": "Direct",
        "applied": "Applied"
    }
    expected_type_to_defaults = {
        "Direct": {"field": None},
        "Generic": {"generic": None},
        "Applied": {"generic": None}
    }
    
    assert result["types"] == expected_name_to_type
    assert result["defaults"] == expected_type_to_defaults
    
    print("✓ Original functionality preserved test passed")


if __name__ == "__main__":
    test_basic_generic_expansion()
    test_multiple_type_parameters()
    test_nested_generic_references()
    test_non_struct_generic()
    test_circular_reference()
    test_wrong_parameter_count()
    test_original_functionality_preserved()
    
    print("\n🎉 All comprehensive tests passed!")
    print("Generic type expansion functionality is working correctly!")
