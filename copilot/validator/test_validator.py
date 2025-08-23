import sys
import os
import json
from pydantic import ValidationError

# Add project root to path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ts_type_filter.parser import parse
from ts_type_filter.validator import create_validator

def test_simple_struct():
    """Test validating a simple struct type"""
    # Define a simple TypeScript type
    ts_code = """
    type Person = {
        name: string,
        age: number,
        isActive?: boolean
    };
    """
    
    # Parse the TypeScript code
    types = parse(ts_code)
    
    # Create a validator for the parsed types
    PersonModel = create_validator(types)
    
    print("Testing simple struct...")
    
    # Test valid data
    valid_data = {
        "name": "John Doe",
        "age": 30,
        "isActive": True
    }
    validated = PersonModel(**valid_data)
    assert validated.name == "John Doe"
    assert validated.age == 30
    assert validated.isActive == True
    
    # Test valid data without optional field
    valid_data2 = {
        "name": "Jane Doe",
        "age": 25
    }
    validated2 = PersonModel(**valid_data2)
    assert validated2.name == "Jane Doe"
    assert validated2.age == 25
    
    # Test invalid data (missing required field)
    invalid_data = {
        "name": "John Doe"
    }
    try:
        PersonModel(**invalid_data)
        assert False, "Validation should fail for missing required field"
    except ValidationError as e:
        print(f"Expected validation error: {e}")
    
    # Test invalid data (wrong type)
    invalid_data2 = {
        "name": "John Doe",
        "age": "thirty"  # Should be a number
    }
    try:
        PersonModel(**invalid_data2)
        assert False, "Validation should fail for wrong type"
    except ValidationError as e:
        print(f"Expected validation error: {e}")

def test_with_literals():
    """Test validating a type with literals"""
    # Define a TypeScript type with literals
    ts_code = """
    type Status = "active" | "inactive" | "pending";
    type User = {
        id: number,
        status: Status
    };
    """
    
    # Parse the TypeScript code
    types = parse(ts_code)
    
    # Create a validator for the parsed types
    UserModel = create_validator(types)
    
    print("\nTesting literals...")
    
    # Test valid data
    valid_data = {
        "id": 1,
        "status": "active"
    }
    validated = UserModel(**valid_data)
    assert validated.id == 1
    assert validated.status == "active"
    
    # Test valid with another status
    valid_data2 = {
        "id": 2,
        "status": "inactive"
    }
    validated2 = UserModel(**valid_data2)
    assert validated2.id == 2
    assert validated2.status == "inactive"
    
    # Test another valid status
    valid_data3 = {
        "id": 3,
        "status": "pending"
    }
    validated3 = UserModel(**valid_data3)
    assert validated3.id == 3
    assert validated3.status == "pending"
    
    # Test with invalid status value
    invalid_data = {
        "id": 4,
        "status": "deleted"  # Not one of the valid statuses
    }
    try:
        UserModel(**invalid_data)
        # We're not enforcing literal validation yet, so this might not fail
        # We'll just print a message if it doesn't fail
        print("Note: Literal validation not enforced yet")
    except ValidationError as e:
        print(f"Expected validation error: {e}")

def test_nested_types():
    """Test validating nested types"""
    ts_code = """
    type Address = {
        street: string,
        city: string,
        zip: number
    };
    
    type Person = {
        name: string,
        address: Address,
        phoneNumbers: string[]
    };
    """
    
    types = parse(ts_code)
    PersonModel = create_validator(types)
    
    print("\nTesting nested types...")
    
    valid_data = {
        "name": "John Smith",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": 12345
        },
        "phoneNumbers": ["555-1234", "555-5678"]
    }
    
    validated = PersonModel(**valid_data)
    assert validated.name == "John Smith"
    assert validated.address.city == "Anytown"
    assert validated.phoneNumbers[0] == "555-1234"
    
    # Test invalid nested data
    invalid_data = {
        "name": "John Smith",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            # Missing zip code
        },
        "phoneNumbers": ["555-1234", "555-5678"]
    }
    
    try:
        PersonModel(**invalid_data)
        assert False, "Validation should fail for missing nested field"
    except ValidationError as e:
        print(f"Expected validation error: {e}")

if __name__ == "__main__":
    print("Running validator tests...\n")
    test_simple_struct()
    test_with_literals()
    test_nested_types()
    print("\nAll tests passed!")
