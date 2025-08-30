import pytest

from pydantic import BaseModel, create_model, Field, field_validator, StringConstraints
import re
from typing import Annotated, Any, List, Literal, Optional, Union as PyUnion


from gotaglio.shared import read_text_file
from ts_type_filter import create_validator, parse
from ts_type_filter import Literal as TSLiteral

# test_cases = [
#     {
#         "source": "type a = 'hello",
#         "root": "a",
#         "sub_cases": [
#             ("hello", True, "matching string literal"),
#             ("other", True, "disallowed string literal"),
#             (123, True, "disallowed number")
#         ],
#         "name": "string literal"
#     }
# ]


def generate_test_cases():
    test_cases = [
        {
            "source": "type a = 'hello'",
            "root": "a",
            "sub_cases": [
                ("hello", True, "matching string literal"),
                ("other", False, "disallowed string literal"),
                (123, False, "disallowed number"),
            ],
            "name": "string literal",
        },
        {
            "source": "type a = 123",
            "root": "a",
            "sub_cases": [
                (123, True, "matching numeric literal"),
                (456, False, "disallowed numeric literal"),
                ("hello", False, "disallowed string"),
            ],
            "name": "numeric literal",
        },
        {
            "source": "type a = true",
            "root": "a",
            "sub_cases": [
                (True, True, "matching boolean literal"),
                (False, False, "disallowed boolean literal"),
                ("hello", False, "disallowed string"),
            ],
            "name": "boolean literal",
        }
    ]

    flattened = []
    ids = []
    for case in test_cases:
        for sub_case in case["sub_cases"]:
            flattened.append(
                (
                    case["source"],
                    case["root"],
                    sub_case[0],  # input_value
                    sub_case[1],  # expected
                    f"{case['name']} - {sub_case[2]}",  # description
                )
            )
            # Create clean test IDs
            test_id = (
                f"{case['name']}_{sub_case[2].replace(' ', '_').replace('-', '_')}"
            )
            ids.append(test_id)
    return flattened, ids


test_params, test_ids = generate_test_cases()


@pytest.mark.parametrize(
    "source,root,input_value,expected,description", test_params, ids=test_ids
)
def test_validator_generated(source, root, input_value, expected, description):
    type_defs = parse(source)
    validator = create_validator2(type_defs, root)
    try:
        # validator.model_validate(input_value)
        validator(value=input_value)
        result = True
    except Exception as e:
        result = False
    assert result == expected, f"Failed test: {description}"

    # Your validation logic here


def create_validator2(types, root_name):
    # types is a list of Node objects, each of which has a `name` parameter
    # find type with matching root_name of None
    root_type = next(
        (t for t in types if t.name == root_name), None
    )
    if not root_type:
        raise ValueError(f"Unknown root type: {root_name}")

    ts_type = root_type.type
    if isinstance(ts_type, TSLiteral):
        # Dynamically create the Literal type
        literal_type = Literal[ts_type.text]
        
        # Use create_model to dynamically create the validator class
        Container = create_model(
            'Container',
            value=(literal_type, ...)
        )
        return Container

        # class Container(BaseModel):
        #     value: Literal[ts_type.text]
        # symbol_table = {t.name: t for t in types}

#     pattern = r"^(" + "|".join(map(re.escape, [ts_type.text])) + r")$"
#     print(pattern)
#     return Annotated[str, StringConstraints(pattern=pattern)]


    # def validate(data):
    #     # Your validation logic here
    #     if data != 'hello':
    #         raise ValueError("Invalid data")

    # return validate


# @pytest.mark.parametrize(
#     "source, expected, test_name", test_cases, ids=[x[2] for x in test_cases]
# )
# def test_cases(source, sub_cases, test_name):
#     tree = parse(source)
#     pass
#     # observed = "\n".join([node.format() for node in tree])
#     # assert (
#     #     observed == expected
#     # ), f"❌ Test Failed: {test_name} | Observed \n{observed}\nExpected \n{expected}"


# def go():
#     ts_source = """
#         type Cart = { items: Item[] };
#         type Item = {
#           required: "A" | "B";
#           optional?: "C" | "D";
#         } | {
#           field1: 1 | 2 | number[];
#           field2: boolean;
#         }
#     """
#     type_def = parse(ts_source)
#     validator = create_validator(type_def, "Cart")

#     x = {"item": []}

#     valid_cases = [
#         ("Cart is empty", {"items": []}, True),
#         ("One item with required field", {"items": [{"required": "A"}]}, True),
#         (
#             "Item with both required and optional fields",
#             {"items": [{"required": "A", "optional": "C"}]},
#             True,
#         ),
#         (
#             "Item with field1 as number and field2 as boolean",
#             {"items": [{"field1": 1, "field2": False}]},
#             True,
#         ),
#         (
#             "Item with field1 as array of numbers and field2 as boolean",
#             {"items": [{"field1": [1, 2, 3], "field2": True}]},
#             True,
#         ),
#     ]

#     invalid_cases = [
#         ("Cart missing `items` field", {}, False),
#         ("Cart is a string literal", {"x": []}, False),
#         ("Items field is not array", {"items": 123}, False),
#         (
#             "Item missing required field but has optional",
#             {"items": [{"optional": "C"}]},
#             False,
#         ),
#         ("Item is a string literal", {"items": ["C"]}, False),
#         (
#             "Item with field1 as array containing a string",
#             {"items": [{"field1": [1, "hello", 3], "field2": False}]},
#             False,
#         ),
#         (
#             "Item with field1 as number not in 1 | 2 and field2 as boolean",
#             {"items": [{"field1": 3, "field2": True}]},
#             False,
#         ),
#     ]

#     print("Valid cases:")
#     process_cases(validator, valid_cases)
#     print("Invalid cases:")
#     process_cases(validator, invalid_cases)


# def process_cases(validator, cases):
#     for title, case_input, expected in cases:
#         try:
#             validator.model_validate(case_input)
#             result = True
#         except Exception as e:
#             result = False

#         print(f"{'  OK:' if result == expected else 'FAIL:'} {title}")
#         if result != expected and expected is False:
#             print("\nWARNING: Expected validation to FAIL, but it PASSED!")
#             # print("Let's examine the model schema:")
#             # schema = validator.model_json_schema()
#             # print(f"Schema: {schema}")

#         # if result == expected:
#         #     print(
#         #         f"Validation passed for input {case_input}: is {'valid' if expected else 'invalid'}"
#         #     )
#         # else:
#         #     print(
#         #         f"Validation failed for input {case_input}: expected {'valid' if expected else 'invalid'}, got {'valid' if result else 'invalid'}"
#         #     )
#     # print("done")


# def go2():
#     ts_source = read_text_file("samples/menu/data/menu.ts")
#     type_def = parse(ts_source)
#     validator = create_validator(type_def, "Cart")

#     cases = [
#         (
#             "has bacon cheeseburger",
#             {
#                 "items": [
#                     {
#                         "name": "Twofer Combo",
#                         "one": {"name": "Bacon Cheeseburger"},
#                         "two": "CHOOSE",
#                     }
#                 ]
#             },
#             True,
#         ),
#         (
#             "has just cheeseburger",
#             {
#                 "items": [
#                     {
#                         "name": "123Two3fer Combo",
#                         "one": {"name": "123Cheeseburger"},
#                         "two": "CHOOSE",
#                     }
#                 ]
#             },
#             False,
#         ),
#     ]

#     process_cases(validator, cases)

# go2()
