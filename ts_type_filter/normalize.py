import copy

# def make_normalizer()

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


# Example usage and test
if __name__ == "__main__":
    # Test with the provided example
    tree = {
        "name": "foo",
        "a": 1,
        "c": {
            "name": "bar"
        }
    }

    defaults = {
        "foo": {"a": 123, "b": 2},
        "bar": {"x": "hello"}
    }

    result = normalize(tree, defaults)
    
    print("Original tree:")
    print(tree)
    print("\nDefaults:")
    print(defaults)
    print("\nNormalized result:")
    print(result)
    
    # Expected result:
    expected = {
        "name": "foo",
        "a": 1,
        "b": 2,
        "c": {
            "name": "bar",
            "x": "hello"
        }
    }
    
    print("\nExpected result:")
    print(expected)
    print(f"\nTest passed: {result == expected}")
