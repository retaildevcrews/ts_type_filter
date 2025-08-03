"""
Debug test for merge_normalizer_specs function.
"""

import sys
import os

from ts_type_filter import merge_normalizer_specs


def debug_merge_with_renames():
    """Debug test merging with type renames."""
    
    original_spec = {
        "types": {"old_name": "OldTypeName"},
        "defaults": {
            "OldTypeName": {"original_field": None, "shared_field": None}
        },
        "duplicates": {}
    }
    
    new_spec = {
        "types": {"new_name": "NewTypeName"},
        "defaults": {
            "NewTypeName": {"new_field": None, "shared_field": None}
        },
        "duplicates": {}
    }
    
    # Rename OldTypeName to NewTypeName
    renamed_types = {"OldTypeName": "NewTypeName"}
    
    merged_spec, warnings = merge_normalizer_specs(new_spec, original_spec, renamed_types)
    
    print("Original spec:", original_spec)
    print("New spec:", new_spec)
    print("Renamed types:", renamed_types)
    print("Merged spec:", merged_spec)
    print("Warnings:", warnings)
    
    # Check defaults - should merge original and new defaults for renamed type
    expected_defaults = {
        "NewTypeName": {
            "original_field": None,  # from original
            "shared_field": None,    # new takes precedence
            "new_field": None        # from new
        }
    }
    print("Expected defaults:", expected_defaults)
    print("Actual defaults:", merged_spec["defaults"])


if __name__ == "__main__":
    debug_merge_with_renames()
