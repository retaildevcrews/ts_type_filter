"""
Integration test showing how create_defaults works with parsed TypeScript.

This demonstrates parsing TypeScript source code and then using create_defaults
to extract the default structure information.
"""

from ts_type_filter import parse
from create_defaults import create_defaults


def test_integration_with_parser():
    """Test create_defaults with TypeScript source code parsed by ts_type_filter."""
    print("=" * 60)
    print("INTEGRATION TEST: Parsing TypeScript → create_defaults")
    print("=" * 60)
    
    # TypeScript source code matching the specification example
    typescript_source = '''
    type Foo = {
        name: "a" | "b";
        field1?: 1;
        field2?: 3;
    };
    
    type Bar = {
        name: "c";
        field3: "hello";
        field4?: 123;
    };
    
    // This type should be ignored since it's not a struct
    type SimpleType = "just_a_string";
    
    // This type has no name field
    type NoName = {
        data: "value";
        optional?: "maybe";
    };
    '''
    
    print("TypeScript source code:")
    print(typescript_source)
    
    # Parse the TypeScript
    print("\nParsing TypeScript...")
    type_defs = parse(typescript_source)
    
    print(f"Parsed {len(type_defs)} type definitions:")
    for type_def in type_defs:
        print(f"  - {type_def.name}: {type_def.format()}")
    
    # Use create_defaults
    print("\nApplying create_defaults...")
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    # Display results
    print("\nResults:")
    print("Name to Type mapping:")
    for name, type_name in sorted(name_to_type.items()):
        print(f'  "{name}" → "{type_name}"')
    
    print("\nType to Defaults mapping:")
    for type_name, defaults in sorted(type_to_defaults.items()):
        print(f'  "{type_name}" → {defaults}')
    
    # Verify against specification
    expected_name_to_type = {
        "a": "Foo",
        "b": "Foo", 
        "c": "Bar"
    }
    
    expected_type_to_defaults = {
        "Foo": {"field1": None, "field2": None},
        "Bar": {"field4": None},
        "NoName": {"optional": None}
    }
    
    print("\nVerification:")
    if name_to_type == expected_name_to_type:
        print("✅ Name to type mapping matches specification!")
    else:
        print(f"❌ Expected: {expected_name_to_type}")
        print(f"❌ Got:      {name_to_type}")
    
    if type_to_defaults == expected_type_to_defaults:
        print("✅ Type to defaults mapping is correct!")
    else:
        print(f"❌ Expected: {expected_type_to_defaults}")
        print(f"❌ Got:      {type_to_defaults}")
    
    return type_defs, name_to_type, type_to_defaults


def test_complex_typescript():
    """Test with more complex TypeScript patterns."""
    print("\n\n" + "=" * 60)
    print("COMPLEX TYPESCRIPT TEST")
    print("=" * 60)
    
    complex_typescript = '''
    // Product catalog types
    type Product = {
        name: ProductName;
        price: number;
        category: "electronics" | "clothing" | "books";
        inStock?: boolean;
        rating?: number;
    };
    
    type ProductName = "Laptop" | "Phone" | "Tablet";
    
    type Customer = {
        name: CustomerType;
        email: string;
        membershipLevel?: "bronze" | "silver" | "gold";
    };
    
    type CustomerType = PersonName;
    type PersonName = "John" | "Jane" | "Bob";
    
    type Order = {
        id: string;
        totalAmount: number;
        items: Product[];
        discount?: number;
        shippingFee?: number;
    };
    '''
    
    print("Complex TypeScript source:")
    print(complex_typescript)
    
    print("\nParsing...")
    type_defs = parse(complex_typescript)
    
    print("\nApplying create_defaults...")
    name_to_type, type_to_defaults = create_defaults(type_defs)
    
    print("\nResults:")
    print("Name mappings:")
    for name, type_name in sorted(name_to_type.items()):
        print(f'  "{name}" → "{type_name}"')
    
    print("\nOptional field mappings:")
    for type_name, defaults in sorted(type_to_defaults.items()):
        print(f'  "{type_name}" → {defaults}')


if __name__ == "__main__":
    test_integration_with_parser()
    test_complex_typescript()
