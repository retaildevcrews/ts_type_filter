from menu import type_defs

def go():
  print("\n\n".join([x.format() for x in type_defs]))

if __name__ == "__main__":
  go()
