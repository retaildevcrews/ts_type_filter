from ts_type_filter import create_validator, parse
from pydantic import ValidationError

def debug_validation(ts_source, type_name, test_data, expected_valid=False):
    """
    Debug why a Pydantic model validates or invalidates a particular input.
    
    Args:
        ts_source: TypeScript type definitions
        type_name: The name of the root type to validate against
        test_data: The data to validate
        expected_valid: Whether the data is expected to be valid
    """
    type_def = parse(ts_source)
    validator = create_validator(type_def, type_name)
    
    print(f"TypeScript Source:\n{ts_source}")
    print(f"\nTest Data:\n{test_data}")
    print(f"\nExpected to be valid: {expected_valid}")
    
    try:
        # Set validate_assignment=True to catch issues with assignment
        # and also show all validation errors with extra detail
        result = validator.model_validate(test_data, strict=True)
        print("\nValidation PASSED ✅")
        print(f"Validated Model: {result}")
        
        if not expected_valid:
            print("\nWARNING: Expected validation to FAIL, but it PASSED!")
            print("Let's examine the model schema:")
            schema = validator.model_json_schema()
            print(f"Schema: {schema}")
    
    except ValidationError as e:
        print("\nValidation FAILED ❌")
        print(f"Validation Error Details:")
        for error in e.errors():
            print(f"  - Location: {error.get('loc', 'unknown')}")
            print(f"    Type: {error.get('type', 'unknown')}")
            print(f"    Message: {error.get('msg', 'unknown')}")
        
        if expected_valid:
            print("\nWARNING: Expected validation to PASS, but it FAILED!")
    
    # Show details about the validator model
    print("\nValidator Model Info:")
    print(f"Model Type: {type(validator)}")
    print("Model Fields:")
    for field_name, field in getattr(validator, "model_fields", {}).items():
        print(f"  - {field_name}: {field}")

# Example usage - You can replace with your specific case
if __name__ == "__main__":
    # Replace with your problematic case
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
    
    # Replace with the data that's causing issues
    test_data = {"items": [{"optional": "C"}]}
    
    # Set to True if you expect this to be valid, False if you expect invalid
    expected_valid = False
    
    debug_validation(ts_source, "Cart", test_data, expected_valid)
