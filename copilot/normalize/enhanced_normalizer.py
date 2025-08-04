"""
Implementation of generic type expansion for create_normalizer_spec.
"""

import sys
import os

# Add the parent directory to sys.path to import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import create_normalizer_spec, _extract_string_literals_from_type
from ts_type_filter.filter import Define, Struct, Union, Literal, Type
import copy


def expand_generic_type(type_node, type_defs, visited=None):
    """
    Expand a generic type reference into its concrete form.
    
    Args:
        type_node: A Type node that might reference a generic type
        type_defs: List of all type definitions
        visited: Set of visited type names to prevent infinite recursion
        
    Returns:
        The expanded type, or None if it cannot be expanded into a struct
    """
    if visited is None:
        visited = set()
    
    if not isinstance(type_node, Type):
        return None
    
    type_name = type_node.name
    type_params = type_node.params or []
    
    if type_name in visited:
        return None
        
    visited.add(type_name)
    
    # Find the generic type definition
    generic_def = None
    for type_def in type_defs:
        if isinstance(type_def, Define) and type_def.name == type_name:
            generic_def = type_def
            break
    
    if not generic_def:
        visited.remove(type_name)
        return None
    
    # Only process if it's a generic with parameters and the referenced type is a Struct
    if not generic_def.params or not isinstance(generic_def.type, Struct):
        visited.remove(type_name)
        return None
    
    # Check if we have the right number of type arguments
    if len(type_params) != len(generic_def.params):
        visited.remove(type_name)
        return None
    
    # Create a mapping from type parameter names to actual types
    param_mapping = {}
    for i, param_def in enumerate(generic_def.params):
        param_name = param_def if isinstance(param_def, str) else param_def.name
        param_mapping[param_name] = type_params[i]
    
    # Substitute type parameters in the struct
    expanded_struct = substitute_type_parameters(generic_def.type, param_mapping)
    
    visited.remove(type_name)
    return expanded_struct


def substitute_type_parameters(node, param_mapping):
    """
    Substitute type parameters in a type node with actual types.
    
    Args:
        node: The type node to process
        param_mapping: Dictionary mapping parameter names to actual types
        
    Returns:
        A new node with type parameters substituted
    """
    if isinstance(node, Type):
        if node.name in param_mapping:
            return param_mapping[node.name]
        else:
            # Recursively substitute in type parameters if any
            new_params = None
            if node.params:
                new_params = [substitute_type_parameters(p, param_mapping) for p in node.params]
            return Type(node.name, new_params)
    
    elif isinstance(node, Struct):
        new_obj = {}
        for field_name, field_type in node.obj.items():
            new_obj[field_name] = substitute_type_parameters(field_type, param_mapping)
        return Struct(new_obj)
    
    elif isinstance(node, Union):
        new_types = [substitute_type_parameters(t, param_mapping) for t in node.types]
        return Union(*new_types)
    
    elif isinstance(node, Literal):
        return node  # Literals don't need substitution
    
    else:
        # For other node types, return as-is
        return node


def create_normalizer_spec_with_generics(type_defs):
    """
    Enhanced version of create_normalizer_spec that handles generic type expansion.
    
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
        struct = None
        
        # Check if it's directly a struct
        if isinstance(type_def.type, Struct):
            struct = type_def.type
        else:
            # Try to expand if it's a generic type reference
            expanded = expand_generic_type(type_def.type, type_defs)
            if expanded and isinstance(expanded, Struct):
                struct = expanded
        
        if not struct:
            continue
        
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
    return {"types": name_to_type, "defaults": type_to_defaults, "duplicates": duplicates}


def test_enhanced_function():
    """Test the enhanced function with the generic type example."""
    
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
    
    result = create_normalizer_spec_with_generics(type_defs)
    name_to_type = result["types"]
    type_to_defaults = result["defaults"]
    duplicates = result["duplicates"]
    
    print("Enhanced function result:")
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
    
    print("Enhanced function test passed!")


if __name__ == "__main__":
    test_enhanced_function()
