import tiktoken

from ts_type_filter import (
    collect_string_literals,
    build_type_index,
    build_filtered_types,
    parse
)

from menu import type_defs as original_type_defs
# from ordering import MenuPipeline

tokenizer = tiktoken.get_encoding("cl100k_base")

# RUNS: 157 tokens
# Read the contents of menu.ts into a string
filename = "samples/menu/junk.ts"
with open(filename, "r", encoding="utf-8") as file:
  type_text1 = file.read()
type_defs1 = parse(type_text1)

# RUNS: 157 tokens
type_text2 = '\n'.join([x.format() for x in original_type_defs])
type_defs2 = parse(type_text2)

# RUNS: 260 tokens
# Adds WiseguyMeal, ComboSizes, CHOOSE, ChooseDrink
type_defs3 = original_type_defs

type_defs = type_defs1

text1 = [x.format() for x in type_defs1]
text2 = [x.format() for x in type_defs2]
text3 = [x.format() for x in type_defs3]

# for i in range(len(text1)):
#   if text1[i] != text2[i]:
#     print(f"=====================> DIFF {i} (1,2):\n'{text1[i]}' != \n'{text2[i]}'\n")
#   if text2[i] != text3[i]:
#     print(f"=====================> DIFF {i} (2,3):\n'{text2[i]}' != \n'{text3[i]}'\n")
#   if text1[i] != text3[i]:
#     print(f"=====================> DIFF {i} (1,3):\n'{text1[i]}' != \n'{text3[i]}'\n")
#   # else:
#   #   print(f"OK {i}:\n'{text1[i]}'\n")

symbols, indexer = build_type_index(type_defs)

def prune(cart, user_query):
  cart_literals = collect_string_literals(cart)
  full_query = [user_query] + cart_literals
  reachable = build_filtered_types(type_defs, symbols, indexer, full_query)
  return reachable

def format(tree):
  text = "\n".join([x.format() for x in tree])
  encoding = tokenizer.encode(text)
  print(f"Tokens: {len(encoding)}\n")
  print(text)


format(prune({"items": [{"name": "Coca-Cola", "size": "Large"}]}, "wiseguy with no tomatoes"))
