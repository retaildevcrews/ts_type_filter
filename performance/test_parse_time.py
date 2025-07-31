#!/usr/bin/env python3
import time
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(__file__))

print("Testing import time...")
start = time.time()

# Import the module that was slow
import ts_type_filter

end = time.time()
print(f"ts_type_filter import time: {end - start:.3f} seconds")

# Read a small TypeScript file to test parsing
with open("samples/menu/data/menu.ts", "r", encoding="utf-8") as f:
    content = f.read()

# Test actual parsing
start = time.time()
from ts_type_filter import parse

# This should trigger the lazy parser compilation
result = parse(content)
end = time.time()
print(f"First parse time (includes lazy compilation): {end - start:.3f} seconds")

# Test parsing again to see if it's faster
start = time.time()
result = parse(content)
end = time.time()
print(f"Second parse time (should be faster): {end - start:.3f} seconds")
