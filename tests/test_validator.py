from gotaglio.shared import read_text_file
from ts_type_filter import create_validator, parse


def go():
    ts_source = """
        type Cart = { items: Item[] };
        type Item = {
          required: "A" | "B";
          optional?: "C" | "D";
        } | {
          field1: 1 | 2 | number[];
          field2: boolean;
        }
    """
    type_def = parse(ts_source)
    validator = create_validator(type_def, "Cart")

    x = {"item": []}

    valid_cases = [
        ("Cart is empty", {"items": []}, True),
        ("One item with required field", {"items": [{"required": "A"}]}, True),
        (
            "Item with both required and optional fields",
            {"items": [{"required": "A", "optional": "C"}]},
            True,
        ),
        (
            "Item with field1 as number and field2 as boolean",
            {"items": [{"field1": 1, "field2": False}]},
            True,
        ),
        (
            "Item with field1 as array of numbers and field2 as boolean",
            {"items": [{"field1": [1, 2, 3], "field2": True}]},
            True,
        ),
    ]

    invalid_cases = [
        ("Cart missing `items` field", {}, False),
        ("Cart is a string literal", {"x": []}, False),
        ("Items field is not array", {"items": 123}, False),
        (
            "Item missing required field but has optional",
            {"items": [{"optional": "C"}]},
            False,
        ),
        ("Item is a string literal", {"items": ["C"]}, False),
        (
            "Item with field1 as array containing a string",
            {"items": [{"field1": [1, "hello", 3], "field2": False}]},
            False,
        ),
        (
            "Item with field1 as number not in 1 | 2 and field2 as boolean",
            {"items": [{"field1": 3, "field2": True}]},
            False,
        ),
    ]

    print("Valid cases:")
    process_cases(validator, valid_cases)
    print("Invalid cases:")
    process_cases(validator, invalid_cases)


def process_cases(validator, cases):
    for title, case_input, expected in cases:
        try:
            validator.model_validate(case_input)
            result = True
        except Exception as e:
            result = False

        print(f"{'  OK:' if result == expected else 'FAIL:'} {title}")
        if result != expected and expected is False:
            print("\nWARNING: Expected validation to FAIL, but it PASSED!")
            # print("Let's examine the model schema:")
            # schema = validator.model_json_schema()
            # print(f"Schema: {schema}")

        # if result == expected:
        #     print(
        #         f"Validation passed for input {case_input}: is {'valid' if expected else 'invalid'}"
        #     )
        # else:
        #     print(
        #         f"Validation failed for input {case_input}: expected {'valid' if expected else 'invalid'}, got {'valid' if result else 'invalid'}"
        #     )
    # print("done")


def go2():
    ts_source = read_text_file("samples/menu/data/menu.ts")
    type_def = parse(ts_source)
    validator = create_validator(type_def, "Cart")

    cases = [
        (
            "has bacon cheeseburger",
            {
                "items": [
                    {
                        "name": "Twofer Combo",
                        "one": {"name": "Bacon Cheeseburger"},
                        "two": "CHOOSE",
                    }
                ]
            },
            True,
        ),
        (
            "has just cheeseburger",
            {
                "items": [
                    {
                        "name": "123Two3fer Combo",
                        "one": {"name": "123Cheeseburger"},
                        "two": "CHOOSE",
                    }
                ]
            },
            False,
        ),
    ]

    process_cases(validator, cases)

go2()
