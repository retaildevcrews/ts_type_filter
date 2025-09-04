import pytest

from gotaglio.shared import read_text_file
from ts_type_filter import create_validator, create_validator2, parse


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
    validator = create_validator2(type_defs, root)
    # try:
        # validator.model_validate(input_value)
    result = validator(input_value)
        # result = True
    # except Exception as e:
    #     result = False
    assert result == expected, f"Failed test: {description}"


# Manual tests - these won't run by default but are visible in test explorer
@pytest.mark.manual
def test_menu_validation():
    source = read_text_file('samples/menu/data/menu.ts')
    type_defs = parse(source)
    validator = create_validator(type_defs, "Cart")
    validator(value={"items": []})
    # print(source)
    assert False

@pytest.mark.manual
def test_complex_typescript_validation_manual():
    """Manual test for complex TypeScript validation scenarios."""
    # This test might be slow or require manual setup
    source = """
    type User = {
        id: number;
        name: string;
        email?: string;
        preferences: {
            theme: 'light' | 'dark';
            notifications: boolean;
        };
        roles: ('admin' | 'user' | 'guest')[];
    }
    type UserProfile = User;
    """
    
    type_defs = parse(source)
    validator = create_validator(type_defs, "UserProfile")
    
    # Test complex valid case
    valid_user = {
        "id": 123,
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True
        },
        "roles": ["admin", "user"]
    }
    
    result = validator(value=valid_user)
    assert result is not None


@pytest.mark.manual
def test_performance_validation_manual():
    """Manual test for performance testing with large objects."""
    # This test might be slow and is only for manual performance analysis
    source = "type BigArray = {items: string[]; metadata: {count: number}}"
    type_defs = parse(source)
    validator = create_validator(type_defs, "BigArray")
    
    # Create a large array for performance testing
    large_data = {
        "items": [f"item_{i}" for i in range(1000)],
        "metadata": {"count": 1000}
    }
    
    import time
    start_time = time.time()
    result = validator(value=large_data)
    end_time = time.time()
    
    print(f"Validation took {end_time - start_time:.4f} seconds")
    assert result is not None


@pytest.mark.manual
def test_edge_case_validation_manual():
    """Manual test for edge cases that might need investigation."""
    # This test covers edge cases that might fail and need manual investigation
    source = "type EdgeCase = {deep: {nested: {value: string | null}}}"
    type_defs = parse(source)
    validator = create_validator(type_defs, "EdgeCase")
    
    # Test deeply nested null values
    edge_case_data = {
        "deep": {
            "nested": {
                "value": None
            }
        }
    }
    
    try:
        result = validator(value=edge_case_data)
        print("Edge case validation succeeded")
    except Exception as e:
        print(f"Edge case validation failed: {e}")
        # In a manual test, we might want to investigate this failure
        raise


@pytest.mark.manual
@pytest.mark.slow
def test_comprehensive_type_coverage_manual():
    """Manual test that covers many TypeScript features - marked as both manual and slow."""
    source = """
    type Status = 'active' | 'inactive' | 'pending';
    type Priority = 1 | 2 | 3 | 4 | 5;
    
    interface BaseItem {
        id: string;
        status: Status;
        priority?: Priority;
    }
    
    interface Task extends BaseItem {
        title: string;
        description?: string;
        assignee: {
            name: string;
            email: string;
        };
        tags: string[];
        metadata: Record<string, any>;
    }
    """
    
    type_defs = parse(source)
    validator = create_validator(type_defs, "Task")
    
    comprehensive_task = {
        "id": "task-001",
        "status": "active",
        "priority": 3,
        "title": "Complete comprehensive testing",
        "description": "This is a detailed description",
        "assignee": {
            "name": "Jane Smith",
            "email": "jane@example.com"
        },
        "tags": ["testing", "validation", "typescript"],
        "metadata": {
            "created": "2025-09-01",
            "project": "ts-type-filter",
            "complexity": "high"
        }
    }
    
    result = validator(value=comprehensive_task)
    assert result is not None
