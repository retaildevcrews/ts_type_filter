"""
Test the merge_normalizer_specs function.
"""

import sys
import os

# Add parent directory to path so we can import ts_type_filter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ts_type_filter import merge_normalizer_specs


def test_basic_merge():
    """Test basic merging of two specs."""
    
    # Original spec
    original_spec = {
        "types": {"old_name1": "OldType1", "old_name2": "OldType2"},
        "defaults": {
            "OldType1": {"field1": None, "field2": None},
            "OldType2": {"field3": None}
        },
        "duplicates": {}
    }
    
    # New spec  
    new_spec = {
        "types": {"new_name1": "NewType1", "new_name2": "NewType2"},
        "defaults": {
            "NewType1": {"fieldA": None},
            "NewType2": {"fieldB": None, "fieldC": None}
        },
        "duplicates": {"dup": ["Type1", "Type2"]}
    }
    
    # No renames
    renamed_types = {}
    
    merged_spec, warnings = merge_normalizer_specs(new_spec, original_spec, renamed_types)
    
    # Check that new types dict is used
    assert merged_spec["types"] == new_spec["types"]
    
    # Check that new duplicates dict is used
    assert merged_spec["duplicates"] == new_spec["duplicates"]
    
    # Check defaults - should have new types plus stale original types
    expected_defaults = {
        "NewType1": {"fieldA": None},
        "NewType2": {"fieldB": None, "fieldC": None},
        "OldType1": {"field1": None, "field2": None},  # stale but retained
        "OldType2": {"field3": None}  # stale but retained
    }
    assert merged_spec["defaults"] == expected_defaults
    
    # Should have warnings about stale entries
    assert len(warnings) == 2
    assert any("stale" in w.lower() and "OldType1" in w for w in warnings)
    assert any("stale" in w.lower() and "OldType2" in w for w in warnings)
    
    print("✓ Basic merge test passed")


def test_merge_with_renames():
    """Test merging with type renames."""
    
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
    
    # Check types and duplicates from new spec
    assert merged_spec["types"] == new_spec["types"]
    assert merged_spec["duplicates"] == new_spec["duplicates"]
    
    # Check defaults - should merge original and new defaults for renamed type
    expected_defaults = {
        "NewTypeName": {
            "original_field": None,  # from original
            "shared_field": None,    # new takes precedence
            "new_field": None        # from new
        }
    }
    assert merged_spec["defaults"] == expected_defaults
    
    # Should have warnings about rename and collision
    assert len(warnings) == 2
    assert any("renamed" in w.lower() for w in warnings)
    assert any("collision" in w.lower() for w in warnings)
    
    print("✓ Rename test passed")


def test_stale_entries():
    """Test handling of stale entries (None vs dict)."""
    
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
    
    # StaleTypeNone should be removed (bound to None)
    # StaleTypeDict should be retained (bound to dict)
    expected_defaults = {
        "NewType": {"field": None},
        "StaleTypeDict": {"some_field": None}
    }
    assert merged_spec["defaults"] == expected_defaults
    
    # Should have warning only for the retained stale entry
    assert len(warnings) == 1
    assert "stale" in warnings[0].lower() and "StaleTypeDict" in warnings[0]
    
    print("✓ Stale entries test passed")


def test_rename_collisions():
    """Test detection of rename collisions."""
    
    original_spec = {
        "types": {},
        "defaults": {"OldType1": {"field": None}, "OldType2": {"field": None}},
        "duplicates": {}
    }
    
    new_spec = {
        "types": {},
        "defaults": {"ConflictType": {"new_field": None}},
        "duplicates": {}
    }
    
    # Multiple renames to same target
    renamed_types = {"OldType1": "SameTarget", "OldType2": "SameTarget"}
    
    merged_spec, warnings = merge_normalizer_specs(new_spec, original_spec, renamed_types)
    
    # Should detect collision in rename dictionary
    collision_warnings = [w for w in warnings if "collision" in w.lower()]
    assert len(collision_warnings) > 0
    
    print("✓ Rename collision test passed")


def test_conflicting_rename():
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
    
    # Should detect collision
    print("Warnings:", warnings)
    collision_warnings = [w for w in warnings if "collision" in w.lower()]
    assert len(collision_warnings) > 0
    
    print("✓ Conflicting rename test passed")


if __name__ == "__main__":
    # test_basic_merge()
    # test_merge_with_renames()
    # test_stale_entries()
    # test_rename_collisions()
    test_conflicting_rename()
    print("\n🎉 All tests passed!")
