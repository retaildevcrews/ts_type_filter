"""
Debug the stale entries test
"""

import sys
import os

# Add parent directory to path so we can import ts_type_filter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ts_type_filter import merge_normalizer_specs


def debug_stale_entries():
    """Debug test handling of stale entries (None vs dict)."""
    
    original_spec = {
        "types": {},
        "defaults": {
            "StaleTypeNone": None,
            "StaleTypeDict": {"some_field": None}
        },
        "duplicates": {}
    }
    
    new_spec = {
        "types": {"new_name": "NewType"},
        "defaults": {"NewType": {"field": None}},
        "duplicates": {}
    }
    
    renamed_types = {}
    
    merged_spec, warnings = merge_normalizer_specs(new_spec, original_spec, renamed_types)
    
    print("Original spec defaults:", original_spec["defaults"])
    print("New spec defaults:", new_spec["defaults"])
    print("Merged spec defaults:", merged_spec["defaults"])
    print("Warnings:", warnings)
    print("Number of warnings:", len(warnings))
    
    # StaleTypeNone should be removed (bound to None)
    # StaleTypeDict should be retained (bound to dict)
    expected_defaults = {
        "NewType": {"field": None},
        "StaleTypeDict": {"some_field": None}
    }
    print("Expected defaults:", expected_defaults)
    print("Defaults match expected:", merged_spec["defaults"] == expected_defaults)
    
    # Should have warning only for the retained stale entry
    print("Test expects 1 warning, got:", len(warnings))


if __name__ == "__main__":
    debug_stale_entries()
