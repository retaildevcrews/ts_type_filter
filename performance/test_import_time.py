#!/usr/bin/env python3
"""
Test script to measure import times for different modules
"""
import time 
import sys
import os

def time_import(module_name, import_statement):
    """Time how long it takes to import a module"""
    start_time = time.time()
    try:
        exec(import_statement)
        end_time = time.time()
        print(f"{module_name}: {end_time - start_time:.3f} seconds")
        return end_time - start_time
    except Exception as e:
        print(f"{module_name}: FAILED - {e}")
        return 0

def main():
    print("Measuring import times...")
    
    # Add the current directory to path like the main script does
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
    
    total_time = 0
    
    # Test individual imports
    times = {}
    times['json'] = time_import('json', 'import json')
    times['os'] = time_import('os', 'import os')
    times['sys'] = time_import('sys', 'import sys')
    times['tiktoken'] = time_import('tiktoken', 'import tiktoken')
    times['lark'] = time_import('lark', 'import lark')
    times['rich.console'] = time_import('rich.console', 'from rich.console import Console')
    times['rich.table'] = time_import('rich.table', 'from rich.table import Table')
    times['rich.text'] = time_import('rich.text', 'from rich.text import Text')
    times['glom'] = time_import('glom', 'from glom import glom')
    
    # Test the heavy ones
    times['ts_type_filter'] = time_import('ts_type_filter', 'import ts_type_filter')
    times['gotaglio.main'] = time_import('gotaglio.main', 'from gotaglio.main import main')
    
    print("\nSummary of import times:")
    for module, import_time in sorted(times.items(), key=lambda x: x[1], reverse=True):
        if import_time > 0:
            print(f"  {module}: {import_time:.3f}s")

if __name__ == "__main__":
    main()
