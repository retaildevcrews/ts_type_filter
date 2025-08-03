"""
Create default values for structs based on type definitions.

This module provides functionality to analyze TypeScript type definitions
and generate default value structures for structs with name fields.
"""
import copy

from .filter import Define, Struct, Union, Literal, Type


def create_normalizer_spec(type_defs):
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
    return {"types": name_to_type, "defaults": type_to_defaults, "duplicates": duplicates}


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


def create_normalizer(spec):
    """
    Create a normalizer function curried with the given spec.
    
    Args:
        spec: The return value of create_defaults(), containing:
            - "types": mapping from name literals to struct type names
            - "defaults": mapping from type names to default field dictionaries
            - "duplicates": any duplicate name literals found
    
    Returns:
        A function that takes only a tree parameter and applies normalization
        using the defaults from the spec
    """
    # Extract the defaults mapping from the spec
    # We need to transform the type-based defaults into name-based defaults
    # that the normalize function expects
    name_to_type = spec.get("types", {})
    type_to_defaults = spec.get("defaults", {})
    
    # Build name-based defaults for the normalize function
    name_based_defaults = {}
    for name, type_name in name_to_type.items():
        if type_name in type_to_defaults:
            name_based_defaults[name] = type_to_defaults[type_name]
    
    # Return the curried function
    def normalizer(tree):
        return normalize(tree, name_based_defaults)
    
    return normalizer

def normalize(tree, defaults):
    """
    Makes a deep copy of tree, replacing any dictionary that has a 'name'
    property with the merge of the default template with that name and the keys
    in the tree. The keys from the tree take precedence.
    
    Args:
        tree: A dictionary whose keys map to primitive types or other trees
        defaults: A dictionary mapping string keys to object templates
    
    Returns:
        A normalized deep copy of the tree
    """
    # Make a deep copy to avoid modifying the original
    result = copy.deepcopy(tree)
    
    def _normalize_recursive(node):
        if isinstance(node, dict):
            # Check if this dictionary has a 'name' property
            if 'name' in node:
                name = node['name']
                # If there's a default template for this name, merge it
                if name in defaults:
                    # Start with the default template
                    merged = copy.deepcopy(defaults[name])
                    # Override with values from the current node (tree takes precedence)
                    merged.update(node)
                    node = merged
            
            # Recursively normalize all values in the dictionary
            for key, value in node.items():
                node[key] = _normalize_recursive(value)
        
        elif isinstance(node, list):
            # Handle lists by normalizing each element
            for i, item in enumerate(node):
                node[i] = _normalize_recursive(item)
        
        # For primitive types, return as-is
        return node
    
    return _normalize_recursive(result)
