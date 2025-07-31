#!/usr/bin/env python3
"""
Test script to verify that parsing still works after lazy loading optimization
"""
import sys
import os

# Add the current directory to path like the main script does
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

def test_parsing():
    print("Testing ts_type_filter parsing functionality...")
    
    # Import the module
    from ts_type_filter import parse
    
    # Test with a simple TypeScript type definition
    test_input = '''
    type Person = {
        name: string;
        age: number;
    };
    
    type Address = {
        street: string;
        city: string;
    };
    '''
    
    # This should trigger the lazy compilation of lark parser
    print("Parsing TypeScript types...")
    result = parse(test_input)
    
    print(f"Successfully parsed {len(result)} type definitions")
    for i, type_def in enumerate(result):
        print(f"  {i+1}. {type_def.name}: {type_def.format()}")
    
    print("✅ Parsing functionality works correctly!")

if __name__ == "__main__":
    test_parsing()
