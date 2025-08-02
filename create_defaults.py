"""
Create default values for structs based on type definitions.

This module provides functionality to analyze TypeScript type definitions
and generate default value structures for structs with name fields.
"""

from ts_type_filter import Define, Struct, Union, Literal, Type


def create_defaults(type_defs):
    """
    Create a data structure for specifying default values for structs.
    
    Args:
        type_defs (list): List of type definitions (Define objects)
        
    Returns:
        tuple: (name_to_type_dict, type_to_defaults_dict)
            - name_to_type_dict: Maps string literals from name fields to struct type names
            - type_to_defaults_dict: Maps type names to dicts of optional fields with None values
            
    Raises:
        ValueError: If duplicate name string literals are found across different struct types
    """
    name_to_type = {}
    type_to_defaults = {}
    
    # Track duplicates for error reporting
    name_to_types_list = {}
    
    for type_def in type_defs:
        if not isinstance(type_def, Define):
            continue
            
        type_name = type_def.name
        
        # Only process struct types
        if not isinstance(type_def.type, Struct):
            continue
            
        struct = type_def.type
        
        # Look for name field in the struct
        name_field = None
        optional_fields = {}
        
        for field_name, field_type in struct.obj.items():
            if field_name == "name":
                name_field = field_type
            elif field_name.endswith("?"):
                # Optional field - add to defaults with None value
                clean_field_name = field_name[:-1]  # Remove the '?' suffix
                optional_fields[clean_field_name] = None
        
        # Store optional fields for this type
        if optional_fields:
            type_to_defaults[type_name] = optional_fields
        
        # Extract string literals from name field
        if name_field:
            name_literals = _extract_string_literals_from_type(name_field, type_defs)
            
            for literal in name_literals:
                # Track for duplicate detection
                if literal not in name_to_types_list:
                    name_to_types_list[literal] = []
                name_to_types_list[literal].append(type_name)
                
                # Add to main mapping
                name_to_type[literal] = type_name
    
    # Check for duplicates
    duplicates = {name: types for name, types in name_to_types_list.items() if len(types) > 1}
    if duplicates:
        duplicate_info = []
        for name, types in duplicates.items():
            duplicate_info.append(f'"{name}" appears in types: {", ".join(types)}')
        raise ValueError(f"Duplicate name string literals found across different struct types:\n" + 
                        "\n".join(duplicate_info))
    
    return name_to_type, type_to_defaults


def _extract_string_literals_from_type(type_node, type_defs, visited=None):
    """
    Extract all string literals from a type, handling unions and type references.
    
    Args:
        type_node: The type node to extract literals from
        type_defs: List of all type definitions for resolving type references
        visited: Set of visited type names to prevent infinite recursion
        
    Returns:
        set: Set of string literals found in the type
    """
    if visited is None:
        visited = set()
    
    literals = set()
    
    if isinstance(type_node, Literal):
        literals.add(type_node.text)
        
    elif isinstance(type_node, Union):
        for union_type in type_node.types:
            literals.update(_extract_string_literals_from_type(union_type, type_defs, visited))
            
    elif isinstance(type_node, Type):
        # Handle type references - look up the actual type definition
        type_name = type_node.name
        
        if type_name in visited:
            # Prevent infinite recursion
            return literals
            
        visited.add(type_name)
        
        # Find the type definition
        for type_def in type_defs:
            if isinstance(type_def, Define) and type_def.name == type_name:
                literals.update(_extract_string_literals_from_type(type_def.type, type_defs, visited))
                break
        
        visited.remove(type_name)
    
    return literals


def main():
    """Example usage of create_defaults function."""
    from ts_type_filter import Define, Struct, Union, Literal, Type
    
    # Example type definitions matching the specification
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
    
    try:
        name_to_type, type_to_defaults = create_defaults(type_defs)
        
        print("Name to Type mapping:")
        for name, type_name in name_to_type.items():
            print(f'  "{name}" -> "{type_name}"')
        
        print("\nType to Defaults mapping:")
        for type_name, defaults in type_to_defaults.items():
            print(f'  "{type_name}" -> {defaults}')
            
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
