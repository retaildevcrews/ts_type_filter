from gotaglio.gotag import read_json_file

def flatten_cases(cases):
  result = []
  for case in cases:
    cart = case["cart"]
    for index, turn in enumerate(case["turns"]):
      step = {
        "uuid": f"{case['uuid']}-{index}",
        "cart": cart,
        "query": turn["query"],
        "expected": turn["expected"],
      }
      cart = turn["expected"]
      result.append(step)
  return result

import json

def go():
  cases = read_json_file("multi_turn_cases.json")    
  result = flatten_cases(cases)
  print(json.dumps(result, indent=2))

go()
