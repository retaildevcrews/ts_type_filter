"""
Comprehensive example demonstrating the create_defaults function.

This example shows how the function works with various TypeScript type patterns
including unions, type references, and optional fields.
"""

from ts_type_filter import Define, Struct, Union, Literal, Type
from create_defaults import create_defaults


def demo_create_defaults():
    """Demonstrate the create_defaults function with a comprehensive example."""
    print("=" * 60)
    print("COMPREHENSIVE DEMO: create_defaults function")
    print("=" * 60)
    
    # Create type definitions that demonstrate various scenarios
    type_defs = [
        # Basic struct with union in name field
        Define("MenuItem", [], Struct({
            "name": Union(Literal("Burger"), Literal("Pizza"), Literal("Salad")),
            "price": Literal(10.99),
            "description?": Literal("A delicious item"),
            "calories?": Literal(500)
        })),
        
        # Struct with single literal name
        Define("Drink", [], Struct({
            "name": Literal("Soda"),
            "size": Literal("Medium"),
            "ice?": Literal(True)
        })),
        
        # Struct with type reference in name field
        Define("Dessert", [], Struct({
            "name": Type("DessertNames"),
            "sweetness": Literal("High"),
            "glutenFree?": Literal(False)
        })),
        
        # Type definition for the reference above
        Define("DessertNames", [], Union(
            Literal("Ice Cream"), 
            Literal("Cake"), 
            Literal("Pie")
        )),
        
        # Struct with nested type reference
        Define("Special", [], Struct({
            "name": Type("SpecialAlias"),
            "available": Literal(True),
            "discount?": Literal(0.1),
            "validUntil?": Literal("2024-12-31")
        })),
        
        # Alias that points to another type
        Define("SpecialAlias", [], Type("SpecialNames")),
        
        # Final type with actual names
        Define("SpecialNames", [], Union(
            Literal("Happy Hour"),
            Literal("Student Discount")
        )),
        
        # Struct with no name field
        Define("Config", [], Struct({
            "setting": Literal("value"),
            "timeout?": Literal(30),
            "retries?": Literal(3)
        })),
        
        # Non-struct type (should be ignored)
        Define("SimpleType", [], Literal("just a string")),
        Define("UnionType", [], Union(Literal("a"), Literal("b"))),
        
        # Struct with no optional fields
        Define("SimpleStruct", [], Struct({
            "name": Literal("Simple Item"),
            "required_field": Literal("always present")
        }))
    ]
    
    # Call the function
    print("Processing type definitions...")
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    # Display results
    print("\n" + "=" * 40)
    print("RESULTS")
    print("=" * 40)
    
    print("\n1. Name to Type Mapping:")
    print("   (Maps string literals from name fields to struct type names)")
    print("   " + "-" * 50)
    for name, type_name in sorted(name_to_type.items()):
        print(f'   "{name}" → "{type_name}"')
    
    print(f"\n   Total mappings: {len(name_to_type)}")
    
    print("\n2. Type to Defaults Mapping:")
    print("   (Maps type names to their optional fields)")
    print("   " + "-" * 50)
    if type_to_defaults:
        for type_name, defaults in sorted(type_to_defaults.items()):
            print(f'   "{type_name}" → {defaults}')
    else:
        print("   (No types have optional fields)")
    
    print(f"\n   Total types with optional fields: {len(type_to_defaults)}")
    
    # Demonstrate the expected structure
    print("\n" + "=" * 40)
    print("EXPECTED STRUCTURE")
    print("=" * 40)
    
    expected_name_to_type = {
        "Burger": "MenuItem",
        "Pizza": "MenuItem", 
        "Salad": "MenuItem",
        "Soda": "Drink",
        "Ice Cream": "Dessert",
        "Cake": "Dessert",
        "Pie": "Dessert",
        "Happy Hour": "Special",
        "Student Discount": "Special",
        "Simple Item": "SimpleStruct"
    }
    
    expected_type_to_defaults = {
        "MenuItem": {"description": None, "calories": None},
        "Drink": {"ice": None},
        "Dessert": {"glutenFree": None},
        "Special": {"discount": None, "validUntil": None},
        "Config": {"timeout": None, "retries": None}
    }
    
    print("\nExpected name_to_type:")
    for name, type_name in sorted(expected_name_to_type.items()):
        print(f'   "{name}" → "{type_name}"')
        
    print("\nExpected type_to_defaults:")
    for type_name, defaults in sorted(expected_type_to_defaults.items()):
        print(f'   "{type_name}" → {defaults}')
    
    # Verify results
    print("\n" + "=" * 40)
    print("VERIFICATION")
    print("=" * 40)
    
    success = True
    
    if name_to_type == expected_name_to_type:
        print("✅ Name to type mapping is correct!")
    else:
        print("❌ Name to type mapping mismatch!")
        print(f"   Expected: {expected_name_to_type}")
        print(f"   Got:      {name_to_type}")
        success = False
    
    if type_to_defaults == expected_type_to_defaults:
        print("✅ Type to defaults mapping is correct!")
    else:
        print("❌ Type to defaults mapping mismatch!")
        print(f"   Expected: {expected_type_to_defaults}")
        print(f"   Got:      {type_to_defaults}")
        success = False
    
    if success:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
    else:
        print("\n❌ Some verifications failed.")
    
    return name_to_type, type_to_defaults


def demo_duplicate_detection():
    """Demonstrate duplicate name detection."""
    print("\n\n" + "=" * 60)
    print("DUPLICATE DETECTION DEMO")
    print("=" * 60)
    
    # Create type definitions with duplicate names
    type_defs_with_duplicates = [
        Define("TypeA", [], Struct({
            "name": Union(Literal("duplicate"), Literal("unique_a")),
            "field_a?": Literal("a")
        })),
        Define("TypeB", [], Struct({
            "name": Union(Literal("duplicate"), Literal("unique_b")),
            "field_b?": Literal("b")
        }))
    ]
    
    print("Testing with duplicate name literals...")
    print('TypeA has names: "duplicate", "unique_a"')
    print('TypeB has names: "duplicate", "unique_b"')
    print('The literal "duplicate" appears in both types.')
    
    try:
        name_to_type, type_to_defaults = create_defaults(type_defs_with_duplicates)
        print("❌ Should have detected duplicates!")
    except ValueError as e:
        print(f"✅ Correctly detected duplicates: {e}")


if __name__ == "__main__":
    demo_create_defaults()
    demo_duplicate_detection()
