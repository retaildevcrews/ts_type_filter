import pytest

from gotaglio.shared import read_text_file
from ts_type_filter import create_validator, parse


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
        },
        {
            "source": "type a = {x: 1, y?: 'hello'}",
            "root": "a",
            "sub_cases": [
                ({"x": 1, "y": "hello"}, True, "required and optional"),
                ({"x": 1}, True, "required only"),
                ({"y": "hello"}, False, "missing required"),
                ({"x": 1, "z": 1}, False, "unexpected field"),
                ({"x": 1, "y": "goodbye"}, False, "incorrect type for y"),
                ({"x": "what", "y": "hello"}, False, "incorrect type for x"),
                ({"x": True, "y": "hello"}, False, "incorrect type for x (2)"),
                ({"x": [True], "y": "hello"}, False, "incorrect type for x (3)"),
            ],
            "name": "struct",
        },
        {
            "source": "type a = {x: 1, y?: 'hello'}[]",
            "root": "a",
            "sub_cases": [
                (
                    [
                        {"x": 1, "y": "hello"},
                        {"x": 1},
                    ],
                    True,
                    "legal element types",
                ),
                ([], True, "empty array"),
                ([1], False, "illegal element type"),
            ],
            "name": "array",
        },
        {
            "source": "type a = 1 | 2 | 'hello'",
            "root": "a",
            "sub_cases": [
                (
                    1,
                    True,
                    "legal element types 1",
                ),
                (
                    2,
                    True,
                    "legal element types 2",
                ),
                (
                    "hello",
                    True,
                    "legal element types 'hello'",
                ),
                (
                    123,
                    False,
                    "illegal element type 123",
                ),
            ],
            "name": "union",
        },
        {
            "source": "type a = boolean",
            "root": "a",
            "sub_cases": [
                (
                    True,
                    True,
                    "legal True",
                ),
                (
                    False,
                    True,
                    "legal False",
                ),
                (
                    1,
                    False,
                    "illegal 1",
                ),
                (
                    0,
                    False,
                    "illegal 0",
                ),
            ],
            "name": "bool",
        },
        {
            "source": "type a = number",
            "root": "a",
            "sub_cases": [
                (
                    123,
                    True,
                    "legal 123",
                ),
                (
                    False,
                    False,
                    "illegal False",
                ),
                (
                    "hello",
                    False,
                    "illegal hello",
                ),
            ],
            "name": "number",
        },
        {
            "source": "type a = string",
            "root": "a",
            "sub_cases": [
                (
                    "hello",
                    True,
                    "legal hello",
                ),
                (
                    False,
                    False,
                    "illegal False",
                ),
                (
                    123,
                    False,
                    "illegal 123",
                ),
            ],
            "name": "string",
        },
        {
            "source": "type a = any",
            "root": "a",
            "sub_cases": [
                (
                    "hello",
                    True,
                    "legal hello",
                ),
                (
                    False,
                    True,
                    "legal False",
                ),
                (
                    123,
                    True,
                    "legal 123",
                ),
            ],
            "name": "any",
        },
        {
            "source": "type a = never",
            "root": "a",
            "sub_cases": [
                (
                    "hello",
                    False,
                    "illegal hello",
                ),
                (
                    False,
                    False,
                    "illegal False",
                ),
                (
                    123,
                    False,
                    "illegal 123",
                ),
            ],
            "name": "never",
        },
        {
            "source": "type a = {x:B, y:C};type B=number;type C=string",
            "root": "a",
            "sub_cases": [
                (
                    {"x": 123, "y": "hello"},
                    True,
                    "legal fields",
                ),
                (
                    {"x": True, "y": "hello"},
                    False,
                    "illegal fields",
                ),
            ],
            "name": "typename",
        },
        {
            "source": "type a = {x:B};type B=C;type C='hello'",
            "root": "a",
            "sub_cases": [
                (
                    {"x": "hello"},
                    True,
                    "legal fields",
                ),
                (
                    {"x": True},
                    False,
                    "illegal fields",
                ),
            ],
            "name": "typename_chaining",
        },
        {
            "source": "type A = B<C,D>;type B<X,Y>={x:X, y:Y};type C=number;type D=string",
            "root": "A",
            "sub_cases": [
                (
                    {"x": 123, "y": "hello"},
                    True,
                    "legal fields",
                ),
                (
                    {"x": True, "y": "hello"},
                    False,
                    "illegal fields",
                ),
            ],
            "name": "generics1",
        },
        {
            "source": "type A = B<C,D>;type B<X,Y>={x:X, y:Y};type C=1;type D='hello'",
            "root": "A",
            "sub_cases": [
                (
                    {"x": 1, "y": "hello"},
                    True,
                    "legal fields",
                ),
                (
                    {"x": True, "y": "hello"},
                    False,
                    "illegal fields",
                ),
            ],
            "name": "generics2",
        },
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
    validator = create_validator(type_defs, root)
    try:
        # validator.model_validate(input_value)
        x = validator(value=input_value)
        result = True
    except Exception as e:
        result = False
    assert result == expected, f"Failed test: {description}"
