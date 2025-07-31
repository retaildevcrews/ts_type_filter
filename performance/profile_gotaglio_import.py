#!/usr/bin/env python3
"""
Profile the gotaglio.main import to see what's taking so long
"""
import sys
import time
import importlib.util

def profile_import_steps():
    """Profile different steps of the import process"""
    print("Profiling gotaglio.main import...")
    
    # Step 1: Just import gotaglio package
    start = time.time()
    try:
        import gotaglio
        step1_time = time.time() - start
        print(f"1. Import gotaglio package: {step1_time:.3f}s")
    except Exception as e:
        print(f"1. Import gotaglio package: FAILED - {e}")
        return
    
    # Step 2: Import gotaglio.main specifically
    start = time.time()
    try:
        from gotaglio.main import main
        step2_time = time.time() - start
        print(f"2. Import gotaglio.main.main: {step2_time:.3f}s")
    except Exception as e:
        print(f"2. Import gotaglio.main.main: FAILED - {e}")
        return
    
    # Step 3: Check what modules are loaded
    gotaglio_modules = [name for name in sys.modules.keys() if 'gotaglio' in name]
    print(f"\nGotaglio modules loaded: {len(gotaglio_modules)}")
    for module in sorted(gotaglio_modules):
        print(f"  - {module}")
    
    # Step 4: Check for heavy dependencies
    heavy_modules = [name for name in sys.modules.keys() if any(heavy in name.lower() for heavy in ['torch', 'tensorflow', 'numpy', 'pandas', 'scipy', 'sklearn', 'transformers', 'openai'])]
    if heavy_modules:
        print(f"\nHeavy dependencies loaded: {len(heavy_modules)}")
        for module in sorted(heavy_modules):
            print(f"  - {module}")
    else:
        print("\nNo obvious heavy dependencies found")

def profile_individual_gotaglio_imports():
    """Try to import individual gotaglio modules to isolate the slow one"""
    print("\n" + "="*50)
    print("Profiling individual gotaglio module imports...")
    
    # Common gotaglio modules based on the grep results
    modules_to_test = [
        'gotaglio.exceptions',
        'gotaglio.helpers', 
        'gotaglio.models',
        'gotaglio.pipeline',
        'gotaglio.repair',
        'gotaglio.shared',
        'gotaglio.dag',
        'gotaglio.director',
        'gotaglio.gotag'
    ]
    
    times = {}
    for module_name in modules_to_test:
        start = time.time()
        try:
            __import__(module_name)
            import_time = time.time() - start
            times[module_name] = import_time
            print(f"{module_name}: {import_time:.3f}s")
        except ImportError as e:
            print(f"{module_name}: FAILED - {e}")
        except Exception as e:
            print(f"{module_name}: ERROR - {e}")
    
    print("\nSlowest gotaglio modules:")
    for module, import_time in sorted(times.items(), key=lambda x: x[1], reverse=True):
        if import_time > 0.01:  # Only show modules taking more than 10ms
            print(f"  {module}: {import_time:.3f}s")

if __name__ == "__main__":
    profile_import_steps()
    profile_individual_gotaglio_imports()
