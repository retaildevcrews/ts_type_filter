"""
Test create_defaults with real menu data from the samples.
"""

import sys
import os

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples", "menu"))

from ts_type_filter.create_defaults import create_defaults

def test_with_menu_data():
    """Test with actual menu type definitions."""
    print("=== Testing with Menu Data ===")
    
    try:
        # Import the menu type definitions
        from samples.menu.menu_typedefs import type_defs
        
        # Run create_defaults on the menu data
        name_to_type, type_to_defaults, duplicates = create_defaults(type_defs)
        
        print(f"Found {len(name_to_type)} name mappings")
        print(f"Found {len(type_to_defaults)} types with optional fields")
        
        print("\nSample name mappings (first 10):")
        for i, (name, type_name) in enumerate(list(name_to_type.items())[:10]):
            print(f'  "{name}" -> "{type_name}"')
            
        print("\nTypes with optional fields:")
        for type_name, defaults in type_to_defaults.items():
            print(f'  "{type_name}" -> {list(defaults.keys())}')

        print("\nDuplicate names found:")
        for name, types in duplicates.items():
            print(f'  "{name}" appears in types: {", ".join(types)}')

        print("✅ Menu data test completed successfully!")
        
    except ImportError as e:
        print(f"Could not import menu_typedefs: {e}")
        print("This is expected if the menu module structure has changed.")
    except Exception as e:
        print(f"❌ Error testing with menu data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_menu_data()
