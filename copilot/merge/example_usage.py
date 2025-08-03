"""
Example usage of merge_normalizer_specs function.
"""

import sys
import os
import json

# Add the parent directory to the path so we can import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import merge_normalizer_specs


def example_usage():
    """
    Demonstrate typical usage of merge_normalizer_specs.
    """
    print("Example: Merging UI Component Specs")
    print("=" * 50)
    
    # Original spec from previous version
    original_spec = {
        "types": {
            "btn": "Button",
            "input": "TextInput", 
            "checkbox": "Checkbox"
        },
        "defaults": {
            "Button": {"enabled": True, "style": "default"},
            "TextInput": {"placeholder": "Enter text", "maxLength": 100},
            "Checkbox": {"checked": False},
            "LegacyDialog": {"modal": True}  # This will be stale
        },
        "duplicates": {}
    }
    
    # New spec from current version
    new_spec = {
        "types": {
            "primary-btn": "PrimaryButton",
            "secondary-btn": "SecondaryButton", 
            "text-field": "TextField",
            "toggle": "Toggle"
        },
        "defaults": {
            "PrimaryButton": {"disabled": False, "variant": "primary"},
            "SecondaryButton": {"disabled": False, "variant": "secondary"},
            "TextField": {"placeholder": "", "required": False, "multiline": False},
            "Toggle": {"checked": False, "size": "medium"}
        },
        "duplicates": {}
    }
    
    # Rename mapping from old to new types
    renamed_types = {
        "Button": "PrimaryButton",      # Old Button becomes PrimaryButton
        "TextInput": "TextField",       # Old TextInput becomes TextField
        "Checkbox": "Toggle"            # Old Checkbox becomes Toggle
    }
    
    print("Original spec types:", list(original_spec["defaults"].keys()))
    print("New spec types:", list(new_spec["defaults"].keys()))
    print("Renames:", renamed_types)
    print()
    
    # Perform the merge
    merged_spec, warnings = merge_normalizer_specs(new_spec, original_spec, renamed_types)
    
    print("MERGE RESULTS:")
    print("-" * 30)
    print("Final types mapping:")
    for name, type_name in merged_spec["types"].items():
        print(f"  '{name}' -> {type_name}")
    
    print("\nFinal defaults:")
    for type_name, defaults in merged_spec["defaults"].items():
        print(f"  {type_name}: {defaults}")
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    
    print("\nAnalysis:")
    print("- PrimaryButton inherited 'enabled' and 'style' from old Button")
    print("- TextField inherited 'maxLength' from old TextInput but new placeholder takes precedence")
    print("- Toggle inherited 'checked' from old Checkbox")
    print("- LegacyDialog was removed due to being stale")
    
    return merged_spec, warnings


if __name__ == "__main__":
    example_usage()
