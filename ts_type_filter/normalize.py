"""
Implementation of generic type expansion for create_normalizer_spec.
"""

import copy
import os
import sys

# Add the parent directory to sys.path to import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.filter import Define, Struct, Union, Literal, Type

def create_normalizer_spec(type_defs):
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
        
        # Extract string literals from name field
        if name_field:
            name_literals = _extract_string_literals_from_type(name_field, type_defs)
            
            # Only store defaults for types that actually have string literals (concrete types)
            if name_literals and optional_fields:
                type_to_defaults[type_name] = optional_fields
            
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


def merge_normalizer_specs(newSpec, originalSpec, renamedTypes):
    """
    Merge two normalizer specs that were produced by create_normalizer_spec().
    
    Args:
        newSpec: The new normalizer spec dictionary containing "types", "defaults", and "duplicates"
        originalSpec: The original normalizer spec dictionary
        renamedTypes: Dictionary mapping old type names to new type names
        
    Returns:
        tuple: (merged_spec, warnings)
            - merged_spec: Dictionary with "types", "defaults", and "duplicates" keys
            - warnings: List of warning strings about renames and stale entries
    """
    warnings = []
    
    # Check for name collisions in renamedTypes
    renamed_targets = {}
    for old_name, new_name in renamedTypes.items():
        if new_name in renamed_targets:
            warnings.append(f"Name collision in renamedTypes: both '{renamed_targets[new_name]}' and '{old_name}' map to '{new_name}'")
        else:
            renamed_targets[new_name] = old_name
    
    # Check for keys in renamedTypes that don't appear in originalSpec defaults
    original_defaults = originalSpec.get("defaults", {})
    for old_name in renamedTypes.keys():
        if old_name not in original_defaults:
            warnings.append(f"Type '{old_name}' in renamedTypes not found in original spec defaults")
    
    # Start with types and duplicates from newSpec
    merged_spec = {
        "types": copy.deepcopy(newSpec.get("types", {})),
        "duplicates": copy.deepcopy(newSpec.get("duplicates", {})),
        "defaults": {}
    }
    
    # Deep copy original defaults and rename keys according to renamedTypes
    renamed_original_defaults = {}
    for type_name, defaults in original_defaults.items():
        new_type_name = renamedTypes.get(type_name, type_name)
        renamed_original_defaults[new_type_name] = copy.deepcopy(defaults)
    
    # Start with renamed original defaults
    merged_defaults = renamed_original_defaults
    
    # Merge in defaults from newSpec
    new_defaults = newSpec.get("defaults", {})
    for type_name, defaults in new_defaults.items():
        if type_name in merged_defaults:
            # Merge default values, with newSpec taking precedence
            merged_entry = copy.deepcopy(merged_defaults[type_name])
            merged_entry.update(defaults)
            merged_defaults[type_name] = merged_entry
        else:
            # New entry - add it
            merged_defaults[type_name] = copy.deepcopy(defaults)
    
    # Check for stale entries from originalSpec that don't appear in newSpec
    stale_types_to_remove = []
    for type_name in renamed_original_defaults.keys():
        if type_name not in new_defaults:
            defaults_value = renamed_original_defaults[type_name]
            # Generate warning
            warnings.append(f"Type '{type_name}' from original spec not found in new spec")
            # Mark for deletion if default value is None or {}
            if defaults_value is None or defaults_value == {}:
                stale_types_to_remove.append(type_name)
    
    # Remove stale types that were marked for deletion
    for type_name in stale_types_to_remove:
        if type_name in merged_defaults:
            del merged_defaults[type_name]
    
    merged_spec["defaults"] = merged_defaults
    
    return merged_spec, warnings



# def test_enhanced_function():
#     """Test the enhanced function with the generic type example."""
    
#     type_defs = [
#         # Generic type definition: OPTION<NAME> = { name: NAME; field1?: number; field2: string; }
#         Define("OPTION", ["NAME"], Struct({
#             "name": Type("NAME"),  # This is a type parameter
#             "field1?": Literal(0),  # optional field with number type
#             "field2": Literal(""),  # required field with string type
#         })),
        
#         # Type that uses the generic: GROUP = OPTION<"a" | "b">
#         Define("GROUP", [], Type("OPTION", [Union(Literal("a"), Literal("b"))])),
#     ]
    
#     result = create_normalizer_spec(type_defs)
#     name_to_type = result["types"]
#     type_to_defaults = result["defaults"]
#     duplicates = result["duplicates"]
    
#     print("Enhanced function result:")
#     print(f"  name_to_type: {name_to_type}")
#     print(f"  type_to_defaults: {type_to_defaults}")
#     print(f"  duplicates: {duplicates}")
    
#     # Now GROUP should be processed correctly
#     expected_name_to_type = {"a": "GROUP", "b": "GROUP"}
#     expected_type_to_defaults = {
#         "OPTION": {"field1": None},  # The original OPTION type
#         "GROUP": {"field1": None}    # The expanded GROUP type
#     }
    
#     assert name_to_type == expected_name_to_type, f"Expected {expected_name_to_type}, got {name_to_type}"
#     assert type_to_defaults == expected_type_to_defaults, f"Expected {expected_type_to_defaults}, got {type_to_defaults}"
#     assert not duplicates, "Expected no duplicate names"
    
#     print("Enhanced function test passed!")


# if __name__ == "__main__":
#     test_enhanced_function()
