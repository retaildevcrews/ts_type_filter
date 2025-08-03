"""
Debug conflicting rename test.
"""

from ts_type_filter import merge_normalizer_specs


def debug_conflicting_rename():
    """Test rename that conflicts with existing type in new spec."""
    
    original_spec = {
        "types": {},
        "defaults": {"OldType": {"old_field": None}},
        "duplicates": {}
    }
    
    new_spec = {
        "types": {},
        "defaults": {"ExistingType": {"new_field": None}},
        "duplicates": {}
    }
    
    # Try to rename to existing type
    renamed_types = {"OldType": "ExistingType"}
    
    merged_spec, warnings = merge_normalizer_specs(new_spec, original_spec, renamed_types)
    
    print("Original spec:", original_spec)
    print("New spec:", new_spec)
    print("Renamed types:", renamed_types)
    print("Merged spec:", merged_spec)
    print("Warnings:", warnings)
    
    # Check for collision warnings
    collision_warnings = [w for w in warnings if "collision" in w.lower()]
    print("Collision warnings:", collision_warnings)


if __name__ == "__main__":
    debug_conflicting_rename()
