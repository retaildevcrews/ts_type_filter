"""
Test cases for merge_normalizer_specs function.
"""

import sys
import os

# Add the parent directory to the path so we can import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter.normalize import merge_normalizer_specs


def test_basic_merge():
    """Test basic merging functionality."""
    print("Testing basic merge...")
    
    newSpec = {
        "types": {"itemA": "TypeA", "itemB": "TypeB"},
        "defaults": {
            "TypeA": {"field1": None, "field2": "default"},
            "TypeB": {"field3": None}
        },
        "duplicates": {}
    }
    
    originalSpec = {
        "types": {"itemX": "TypeX", "itemY": "TypeY"},
        "defaults": {
            "TypeX": {"fieldX": None},
            "TypeY": {"fieldY": "oldDefault", "field2": "original"}
        },
        "duplicates": {}
    }
    
    renamedTypes = {"TypeY": "TypeA"}
    
    merged_spec, warnings = merge_normalizer_specs(newSpec, originalSpec, renamedTypes)
    
    print("Merged spec:", merged_spec)
    print("Warnings:", warnings)
    
    # Check that types and duplicates come from newSpec
    assert merged_spec["types"] == newSpec["types"]
    assert merged_spec["duplicates"] == newSpec["duplicates"]
    
    # Check that TypeA merged properly (TypeY renamed to TypeA and merged with newSpec TypeA)
    expected_typeA_defaults = {
        "fieldY": "oldDefault",  # from original TypeY
        "field2": "default",     # from new TypeA (takes precedence)
        "field1": None           # from new TypeA
    }
    assert merged_spec["defaults"]["TypeA"] == expected_typeA_defaults
    
    # Check that TypeB is preserved from newSpec
    assert merged_spec["defaults"]["TypeB"] == {"field3": None}
    
    # Check that TypeX is preserved but generates warning (stale entry)
    assert "TypeX" in [w for w in warnings if "not found in new spec" in w][0]
    
    print("✓ Basic merge test passed")


def test_name_collisions():
    """Test detection of name collisions in renamedTypes."""
    print("\nTesting name collisions...")
    
    newSpec = {
        "types": {},
        "defaults": {},
        "duplicates": {}
    }
    
    originalSpec = {
        "types": {},
        "defaults": {
            "TypeA": {"field1": None},
            "TypeB": {"field2": None}
        },
        "duplicates": {}
    }
    
    # Both TypeA and TypeB rename to TypeC
    renamedTypes = {"TypeA": "TypeC", "TypeB": "TypeC"}
    
    merged_spec, warnings = merge_normalizer_specs(newSpec, originalSpec, renamedTypes)
    
    print("Warnings:", warnings)
    
    # Should have a warning about name collision
    collision_warnings = [w for w in warnings if "Name collision" in w]
    assert len(collision_warnings) == 1
    assert "TypeC" in collision_warnings[0]
    
    print("✓ Name collision test passed")


def test_missing_renamed_types():
    """Test warnings for renamed types not in original spec."""
    print("\nTesting missing renamed types...")
    
    newSpec = {
        "types": {},
        "defaults": {},
        "duplicates": {}
    }
    
    originalSpec = {
        "types": {},
        "defaults": {
            "TypeA": {"field1": None}
        },
        "duplicates": {}
    }
    
    # Try to rename TypeB which doesn't exist in original
    renamedTypes = {"TypeB": "TypeC"}
    
    merged_spec, warnings = merge_normalizer_specs(newSpec, originalSpec, renamedTypes)
    
    print("Warnings:", warnings)
    
    # Should have a warning about missing type
    missing_warnings = [w for w in warnings if "not found in original spec" in w]
    assert len(missing_warnings) == 1
    assert "TypeB" in missing_warnings[0]
    
    print("✓ Missing renamed types test passed")


def test_stale_entry_deletion():
    """Test deletion of stale entries with None or {} values."""
    print("\nTesting stale entry deletion...")
    
    newSpec = {
        "types": {},
        "defaults": {},
        "duplicates": {}
    }
    
    originalSpec = {
        "types": {},
        "defaults": {
            "TypeA": None,           # Should be deleted
            "TypeB": {},             # Should be deleted
            "TypeC": {"field": None} # Should be kept despite warning
        },
        "duplicates": {}
    }
    
    renamedTypes = {}
    
    merged_spec, warnings = merge_normalizer_specs(newSpec, originalSpec, renamedTypes)
    
    print("Merged defaults:", merged_spec["defaults"])
    print("Warnings:", warnings)
    
    # TypeA and TypeB should be deleted
    assert "TypeA" not in merged_spec["defaults"]
    assert "TypeB" not in merged_spec["defaults"]
    
    # TypeC should be kept
    assert "TypeC" in merged_spec["defaults"]
    assert merged_spec["defaults"]["TypeC"] == {"field": None}
    
    # Should have warnings for all three
    stale_warnings = [w for w in warnings if "not found in new spec" in w]
    assert len(stale_warnings) == 3
    
    print("✓ Stale entry deletion test passed")


def test_complex_merge():
    """Test a more complex merge scenario."""
    print("\nTesting complex merge scenario...")
    
    newSpec = {
        "types": {
            "button": "Button",
            "input": "Input",
            "select": "Select"
        },
        "defaults": {
            "Button": {"disabled": False, "type": "button"},
            "Input": {"placeholder": "", "required": False},
            "Select": {"multiple": False}
        },
        "duplicates": {}
    }
    
    originalSpec = {
        "types": {
            "old_button": "OldButton",
            "old_input": "OldInput"
        },
        "defaults": {
            "OldButton": {"enabled": True, "style": "default"},
            "OldInput": {"placeholder": "Enter text", "maxLength": 100},
            "ObsoleteType": {"obsolete": True}  # Should trigger warning
        },
        "duplicates": {}
    }
    
    renamedTypes = {
        "OldButton": "Button",
        "OldInput": "Input"
    }
    
    merged_spec, warnings = merge_normalizer_specs(newSpec, originalSpec, renamedTypes)
    
    print("Final merged spec:")
    for key, value in merged_spec.items():
        print(f"  {key}: {value}")
    print("Warnings:", warnings)
    
    # Verify types and duplicates from newSpec
    assert merged_spec["types"] == newSpec["types"]
    assert merged_spec["duplicates"] == newSpec["duplicates"]
    
    # Verify Button merge (OldButton renamed to Button)
    expected_button = {
        "enabled": True,       # from original OldButton
        "style": "default",    # from original OldButton
        "disabled": False,     # from new Button (takes precedence if there was conflict)
        "type": "button"       # from new Button
    }
    assert merged_spec["defaults"]["Button"] == expected_button
    
    # Verify Input merge (OldInput renamed to Input)
    expected_input = {
        "placeholder": "",     # from new Input (takes precedence)
        "maxLength": 100,      # from original OldInput
        "required": False      # from new Input
    }
    assert merged_spec["defaults"]["Input"] == expected_input
    
    # Verify Select is preserved from newSpec
    assert merged_spec["defaults"]["Select"] == {"multiple": False}
    
    # Verify ObsoleteType generates warning but is preserved (not None or {})
    assert "ObsoleteType" in merged_spec["defaults"]
    obsolete_warnings = [w for w in warnings if "ObsoleteType" in w and "not found in new spec" in w]
    assert len(obsolete_warnings) == 1
    
    print("✓ Complex merge test passed")


if __name__ == "__main__":
    test_basic_merge()
    test_name_collisions()
    test_missing_renamed_types()
    test_stale_entry_deletion()
    test_complex_merge()
    print("\n🎉 All tests passed!")
