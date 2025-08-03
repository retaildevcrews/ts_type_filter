"""
Test the create_defaults function with various scenarios.
"""

import sys
import os
import pytest

# # Add the current directory to sys.path so we can import create_defaults
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ts_type_filter import create_defaults
from ts_type_filter import Define, Struct, Union, Literal, Type


def test_basic_example():
    """Test the basic example from the specification."""
    
    type_defs = [
        Define("Foo", [], Struct({
            "name": Union(Literal("a"), Literal("b")),
            "field1?": Literal(1),
            "field2?": Literal(3)
        })),
        Define("Bar", [], Struct({
            "name": Literal("c"),
            "field3": Literal("hello"),
            "field4?": Literal(123)
        }))
    ]
    
    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    
    expected_name_to_type = {"a": "Foo", "b": "Foo", "c": "Bar"}
    expected_type_to_defaults = {
        "Foo": {"field1": None, "field2": None},
        "Bar": {"field4": None}
    }
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"


def test_type_references():
    """Test type references in name fields."""
    
    type_defs = [
        Define("MyStruct", [], Struct({
            "name": Type("MyNames"),
            "optional_field?": Literal("value")
        })),
        Define("MyNames", [], Union(Literal("name1"), Literal("name2"))),
        # Define("AnotherStruct", [], Struct({
        #     "name": Type("MyNames"),  # Same type reference - should cause duplicate error
        #     "other_field?": Literal(42)
        # }))
    ]

    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    expected_name_to_type = {'name2': 'MyStruct', 'name1': 'MyStruct'}
    expected_type_to_defaults = {'MyStruct': {'optional_field': None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"

    # with pytest.raises(ValueError, match="(?i)duplicate"):
    #     create_defaults(type_defs)


def test_nested_type_references():
    """Test nested type references."""
    
    type_defs = [
        Define("MainStruct", [], Struct({
            "name": Type("NameAlias"),
            "required_field": Literal("required"),
            "optional_field?": Literal("optional")
        })),
        Define("NameAlias", [], Type("ActualNames")),
        Define("ActualNames", [], Union(Literal("deep1"), Literal("deep2")))
    ]
    
    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    
    expected_name_to_type = {"deep1": "MainStruct", "deep2": "MainStruct"}
    expected_type_to_defaults = {"MainStruct": {"optional_field": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"


def test_no_optional_fields():
    """Test struct with no optional fields."""
    
    type_defs = [
        Define("SimpleStruct", [], Struct({
            "name": Literal("simple"),
            "required_field": Literal("required")
        }))
    ]
    
    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    
    expected_name_to_type = {"simple": "SimpleStruct"}
    expected_type_to_defaults = {}  # No optional fields
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"


def test_no_name_field():
    """Test struct with no name field."""
    
    type_defs = [
        Define("NoNameStruct", [], Struct({
            "other_field": Literal("value"),
            "optional_field?": Literal("optional")
        }))
    ]
    
    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    
    expected_name_to_type = {}  # No name field
    expected_type_to_defaults = {"NoNameStruct": {"optional_field": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"


def test_non_struct_types():
    """Test that non-struct types are ignored."""

    type_defs = [
        Define("SimpleType", [], Literal("just_a_literal")),
        Define("UnionType", [], Union(Literal("a"), Literal("b"))),
        Define("StructType", [], Struct({
            "name": Literal("struct_name"),
            "optional?": Literal("value")
        }))
    ]
    
    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    
    expected_name_to_type = {"struct_name": "StructType"}
    expected_type_to_defaults = {"StructType": {"optional": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    assert not duplicates, "Expected no duplicate names"

def test_duplicate_names():
    """Test handling of duplicate names across different structs."""
    
    type_defs = [
        Define("FirstStruct", [], Struct({
            "name": Literal("duplicate"),
            "optional_field?": Literal("value1")
        })),
        Define("SecondStruct", [], Struct({
            "name": Literal("duplicate"),  # Duplicate name
            "another_field?": Literal("value2")
        }))
    ]

    name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
    assert duplicates == {"duplicate": ["FirstStruct", "SecondStruct"]}
    # with pytest.raises(ValueError, match="Duplicate name string literals found: 'duplicate'"):
    #     create_defaults(type_defs)