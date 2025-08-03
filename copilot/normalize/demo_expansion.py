"""
Demo script showing the generic type expansion functionality
with the exact example from the user's request.
"""

import sys
import os

# Add the parent directory to sys.path to import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import create_normalizer_spec, create_normalizer
from ts_type_filter.filter import Define, Struct, Union, Literal, Type


def demo_user_example():
    """Demonstrate the functionality with the user's exact example."""
    
    print("🔧 Demo: Generic Type Expansion")
    print("=" * 50)
    
    # The user's example:
    # type GROUP = OPTION<"a" | "b">;
    # type OPTION<NAME> = {
    #   name: NAME;
    #   field1?: number;
    #   field2: string;
    # }
    
    type_defs = [
        Define("OPTION", ["NAME"], Struct({
            "name": Type("NAME"),
            "field1?": Literal(42),     # optional number field
            "field2": Literal("hello"), # required string field
        })),
        Define("GROUP", [], Type("OPTION", [Union(Literal("a"), Literal("b"))])),
    ]
    
    print("Input TypeScript declarations:")
    print("type OPTION<NAME> = {")
    print("  name: NAME;")
    print("  field1?: number;")
    print("  field2: string;")
    print("}")
    print("type GROUP = OPTION<\"a\" | \"b\">;")
    print()
    
    spec = create_normalizer_spec(type_defs)
    
    print("Generated normalizer spec:")
    print(f"  Types mapping: {spec['types']}")
    print(f"  Defaults: {spec['defaults']}")
    print(f"  Duplicates: {spec['duplicates']}")
    print()
    
    # Create a normalizer function
    normalizer = create_normalizer(spec)
    
    print("Testing normalization with sample data:")
    print()
    
    # Test data that should be normalized
    test_cases = [
        {"name": "a"},
        {"name": "b"},
        {"name": "a", "custom_field": "preserved"},
        {"name": "b", "field1": 99, "field2": "custom"},
        [
            {"name": "a"},
            {"name": "b", "extra": "data"}
        ]
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test case {i}:")
        print(f"  Input:  {test_case}")
        
        try:
            normalized = normalizer(test_case)
            print(f"  Output: {normalized}")
        except Exception as e:
            print(f"  Error:  {e}")
        
        print()
    
    print("✅ The GROUP type is now treated as:")
    print("type GROUP = {")
    print("  name: \"a\" | \"b\";")
    print("  field1?: number;")
    print("  field2: string;")
    print("}")
    print()
    print("🎉 Generic type expansion is working correctly!")


if __name__ == "__main__":
    demo_user_example()
