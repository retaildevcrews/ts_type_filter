from rich import print
import sys
import inverted
import sonnets

def go():
  # Create an index
  index = inverted.Index()

  # Add sonnets to the index
  for sonnet in sonnets.sonnets:
    index.add(sonnet)

  index.statistics()

if __name__ == "__main__":
  go()
