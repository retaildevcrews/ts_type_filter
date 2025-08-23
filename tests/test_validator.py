from ts_type_filter import create_validator, parse


def go():
    ts_source = """
        type Cart = { items: Item[] };
        type Item = "A" | "B"
    """
    type_def = parse(ts_source)
    validator = create_validator(type_def, "Cart")

    x = {"item": []}

    cases = [
        ({}, False),
        ({"x": []}, False),
        ({"items": []}, True),
        ({"items": 123}, False),
        ({"items": ["A", "B"]}, True),

        # This should fail validation because "C" is not a valid Item according to ts_source
        ({"items": ["C"]}, False),
    ]

    for case_input, expected in cases:
        try:
            validator.model_validate(case_input)
            result = True
        except Exception as e:
            result = False

        if result == expected:
            print(f"Validation passed for input {case_input}: is {'valid' if expected else 'invalid'}")
        else:
            print(f"Validation failed for input {case_input}: expected {'valid' if expected else 'invalid'}, got {'valid' if result else 'invalid'}")
    print("done")


go()
"print(f'Literal values: {literal_values}')"  
