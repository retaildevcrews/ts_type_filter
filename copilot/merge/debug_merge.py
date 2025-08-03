"""
Debug utilities for merge_normalizer_specs function.
"""

import sys
import os

# Add the parent directory to the path so we can import ts_type_filter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gotaglio.shared import to_json_string
from ts_type_filter.normalize import merge_normalizer_specs


def debug_merge_step_by_step(newSpec, originalSpec, renamedTypes):
    """
    Debug the merge process step by step with detailed output.
    """
    print("=" * 80)
    print("DEBUGGING MERGE_NORMALIZER_SPECS")
    print("=" * 80)
    
    print("\nInput Parameters:")
    print("-" * 40)
    print("newSpec:")
    print(to_json_string(newSpec))
    print("\noriginalSpec:")
    print(to_json_string(originalSpec))
    print("\nrenamedTypes:")
    print(to_json_string(renamedTypes))
    
    print("\n" + "=" * 80)
    print("STEP-BY-STEP EXECUTION")
    print("=" * 80)
    
    # Step 1: Check for name collisions
    print("\nStep 1: Checking for name collisions in renamedTypes")
    print("-" * 50)
    warnings = []
    renamed_targets = {}
    
    for old_name, new_name in renamedTypes.items():
        if new_name in renamed_targets:
            collision_warning = f"Name collision in renamedTypes: both '{renamed_targets[new_name]}' and '{old_name}' map to '{new_name}'"
            warnings.append(collision_warning)
            print(f"🚨 COLLISION: {collision_warning}")
        else:
            renamed_targets[new_name] = old_name
            print(f"✓ {old_name} -> {new_name}")
    
    if not renamedTypes:
        print("No renames specified")
    
    # Step 2: Check for missing types in original spec
    print("\nStep 2: Checking for missing types in original spec")
    print("-" * 50)
    original_defaults = originalSpec.get("defaults", {})
    
    for old_name in renamedTypes.keys():
        if old_name not in original_defaults:
            missing_warning = f"Type '{old_name}' in renamedTypes not found in original spec defaults"
            warnings.append(missing_warning)
            print(f"🚨 MISSING: {missing_warning}")
        else:
            print(f"✓ {old_name} found in original spec")
    
    # Step 3: Initialize merged spec with newSpec data
    print("\nStep 3: Initializing merged spec with newSpec data")
    print("-" * 50)
    merged_spec = {
        "types": newSpec.get("types", {}).copy(),
        "duplicates": newSpec.get("duplicates", {}).copy(),
        "defaults": {}
    }
    print(f"types: {merged_spec['types']}")
    print(f"duplicates: {merged_spec['duplicates']}")
    
    # Step 4: Rename original defaults
    print("\nStep 4: Renaming original defaults according to renamedTypes")
    print("-" * 50)
    renamed_original_defaults = {}
    
    for type_name, defaults in original_defaults.items():
        new_type_name = renamedTypes.get(type_name, type_name)
        renamed_original_defaults[new_type_name] = defaults.copy() if defaults else defaults
        if type_name in renamedTypes:
            print(f"✓ Renamed {type_name} -> {new_type_name}: {defaults}")
        else:
            print(f"✓ Kept {type_name}: {defaults}")
    
    print(f"Renamed original defaults: {renamed_original_defaults}")
    
    # Step 5: Start with renamed original defaults
    print("\nStep 5: Starting with renamed original defaults")
    print("-" * 50)
    merged_defaults = renamed_original_defaults.copy()
    print(f"Initial merged defaults: {merged_defaults}")
    
    # Step 6: Merge in newSpec defaults
    print("\nStep 6: Merging in newSpec defaults")
    print("-" * 50)
    new_defaults = newSpec.get("defaults", {})
    
    for type_name, defaults in new_defaults.items():
        if type_name in merged_defaults:
            print(f"🔄 Merging {type_name}:")
            print(f"   Original: {merged_defaults[type_name]}")
            print(f"   New:      {defaults}")
            merged_entry = merged_defaults[type_name].copy() if merged_defaults[type_name] else {}
            merged_entry.update(defaults)
            merged_defaults[type_name] = merged_entry
            print(f"   Result:   {merged_entry}")
        else:
            print(f"➕ Adding new type {type_name}: {defaults}")
            merged_defaults[type_name] = defaults.copy() if defaults else defaults
    
    # Step 7: Check for stale entries
    print("\nStep 7: Checking for stale entries")
    print("-" * 50)
    for type_name in renamed_original_defaults.keys():
        if type_name not in new_defaults:
            defaults_value = renamed_original_defaults[type_name]
            stale_warning = f"Type '{type_name}' from original spec not found in new spec"
            warnings.append(stale_warning)
            print(f"🚨 STALE: {stale_warning}")
            
            if defaults_value is None or defaults_value == {}:
                print(f"   🗑️  Deleting {type_name} (value is {defaults_value})")
                if type_name in merged_defaults:
                    del merged_defaults[type_name]
            else:
                print(f"   ⚠️  Keeping {type_name} (value is {defaults_value})")
    
    merged_spec["defaults"] = merged_defaults
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print("Merged spec:")
    print(to_json_string(merged_spec))
    print("\nWarnings:")
    for i, warning in enumerate(warnings, 1):
        print(f"{i}. {warning}")
    
    print("\n" + "=" * 80)
    
    return merged_spec, warnings


def create_sample_scenario():
    """Create a sample scenario for debugging."""
    print("Creating sample debugging scenario...")
    
    newSpec = {
        "types": {
            "submit": "SubmitButton",
            "cancel": "CancelButton",
            "text": "TextInput"
        },
        "defaults": {
            "SubmitButton": {"disabled": False, "type": "submit"},
            "CancelButton": {"disabled": False, "variant": "secondary"},
            "TextInput": {"placeholder": "", "required": False}
        },
        "duplicates": {}
    }
    
    originalSpec = {
        "types": {
            "old_submit": "Button",
            "old_text": "Input"
        },
        "defaults": {
            "Button": {"enabled": True, "style": "primary"},
            "Input": {"placeholder": "Enter value", "maxLength": 50},
            "LegacyWidget": None,  # Should be deleted
            "DeprecatedComponent": {}  # Should be deleted
        },
        "duplicates": {}
    }
    
    renamedTypes = {
        "Button": "SubmitButton",
        "Input": "TextInput"
    }
    
    return debug_merge_step_by_step(newSpec, originalSpec, renamedTypes)


if __name__ == "__main__":
    create_sample_scenario()
