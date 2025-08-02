"""
Test the create_defaults function with various scenarios.
"""

import sys
import os

# Add the current directory to sys.path so we can import create_defaults
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_defaults import create_defaults
from ts_type_filter import Define, Struct, Union, Literal, Type


def test_basic_example():
    """Test the basic example from the specification."""
    print("=== Testing Basic Example ===")
    
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
    
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    expected_name_to_type = {"a": "Foo", "b": "Foo", "c": "Bar"}
    expected_type_to_defaults = {
        "Foo": {"field1": None, "field2": None},
        "Bar": {"field4": None}
    }
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    
    print("✅ Basic example test passed!")


def test_type_references():
    """Test type references in name fields."""
    print("\n=== Testing Type References ===")
    
    type_defs = [
        Define("MyStruct", [], Struct({
            "name": Type("MyNames"),
            "optional_field?": Literal("value")
        })),
        Define("MyNames", [], Union(Literal("name1"), Literal("name2"))),
        Define("AnotherStruct", [], Struct({
            "name": Type("MyNames"),  # Same type reference - should cause duplicate error
            "other_field?": Literal(42)
        }))
    ]
    
    try:
        name_to_type, type_to_defaults = create_defaults(type_defs)
        print("❌ Should have raised ValueError for duplicates")
    except ValueError as e:
        print(f"✅ Correctly detected duplicate names: {e}")


def test_nested_type_references():
    """Test nested type references."""
    print("\n=== Testing Nested Type References ===")
    
    type_defs = [
        Define("MainStruct", [], Struct({
            "name": Type("NameAlias"),
            "required_field": Literal("required"),
            "optional_field?": Literal("optional")
        })),
        Define("NameAlias", [], Type("ActualNames")),
        Define("ActualNames", [], Union(Literal("deep1"), Literal("deep2")))
    ]
    
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    expected_name_to_type = {"deep1": "MainStruct", "deep2": "MainStruct"}
    expected_type_to_defaults = {"MainStruct": {"optional_field": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    
    print("✅ Nested type references test passed!")


def test_no_optional_fields():
    """Test struct with no optional fields."""
    print("\n=== Testing No Optional Fields ===")
    
    type_defs = [
        Define("SimpleStruct", [], Struct({
            "name": Literal("simple"),
            "required_field": Literal("required")
        }))
    ]
    
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    expected_name_to_type = {"simple": "SimpleStruct"}
    expected_type_to_defaults = {}  # No optional fields
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    
    print("✅ No optional fields test passed!")


def test_no_name_field():
    """Test struct with no name field."""
    print("\n=== Testing No Name Field ===")
    
    type_defs = [
        Define("NoNameStruct", [], Struct({
            "other_field": Literal("value"),
            "optional_field?": Literal("optional")
        }))
    ]
    
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    expected_name_to_type = {}  # No name field
    expected_type_to_defaults = {"NoNameStruct": {"optional_field": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    
    print("✅ No name field test passed!")


def test_non_struct_types():
    """Test that non-struct types are ignored."""
    print("\n=== Testing Non-Struct Types ===")
    
    type_defs = [
        Define("SimpleType", [], Literal("just_a_literal")),
        Define("UnionType", [], Union(Literal("a"), Literal("b"))),
        Define("StructType", [], Struct({
            "name": Literal("struct_name"),
            "optional?": Literal("value")
        }))
    ]
    
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    expected_name_to_type = {"struct_name": "StructType"}
    expected_type_to_defaults = {"StructType": {"optional": None}}
    
    assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
    assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
    
    print("✅ Non-struct types test passed!")


if __name__ == "__main__":
    test_basic_example()
    test_nested_type_references()
    test_no_optional_fields()
    test_no_name_field()
    test_non_struct_types()
    test_type_references()  # This should be last since it raises an exception
    
    print("\n🎉 All tests completed!")
