import os
from rich import print
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ts_type_filter import Index

import sonnets

def go():
  # Create an index
  index = Index()

  # Add sonnets to the index
  for sonnet in sonnets.sonnets:
    index.add(sonnet)

  index.statistics()

if __name__ == "__main__":
  go()
