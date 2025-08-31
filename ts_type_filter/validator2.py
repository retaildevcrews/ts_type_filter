from pydantic import (
    BaseModel,
    ConfigDict,
    create_model,
    Field,
    field_validator,
    StringConstraints,
    BeforeValidator,
)
from typing import Annotated, Any, List, Literal, Never, Optional, Type, Union

from ts_type_filter import (
    Any as TS_Any,
    Array as TS_Array,
    Define as TS_Define,
    Literal as TS_Literal,
    Never as TS_Never,
    Struct as TS_Struct,
    Union as TS_Union,
    Type as TS_Type,
)


def create_validator3(types, root_name):
    # Build symbol table for all type definitions
    symbol_table = {}
    for t in types:
        if isinstance(t, TS_Define):
            symbol_table[t.name] = t

    # Find the root type definition based on root_name
    if root_name in symbol_table:
        root_type = symbol_table[root_name]
    else:
        raise ValueError(
            f"Root type '{root_name}' not found in type definitions"
        )  # Keep track of models we've already created to avoid recursion issues

    created_models = {}

    # Recursive function to convert TypeScript types to Pydantic types
    def convert_type(ts_type, required=True, path=""):
        if isinstance(ts_type, TS_Type):
            if ts_type.name in symbol_table:
                if ts_type.name not in created_models:
                    type_def = symbol_table[ts_type.name]
                    model_type = convert_type(type_def.type)
                    created_models[ts_type.name] = model_type
                return created_models[ts_type.name]
            elif ts_type.name == "string":
                return str
            elif ts_type.name == "number":
                return float  # Using float for all numbers for simplicity
            elif ts_type.name == "boolean":
                return bool
            elif ts_type.name == "any":
                return Any
            elif ts_type.name == "never":
                def never_validator(v):
                    raise ValueError("Never type should never have a value")
                return Annotated[Any, BeforeValidator(never_validator)]
            else:
                raise ValueError(f"Unknown type: {ts_type.name}")
        elif isinstance(ts_type, TS_Literal):
            # Create a strict validator that checks exact type and value
            literal_value = ts_type.text
            literal_type = type(literal_value)
            
            def create_strict_validator(expected_value, expected_type):
                def validator(v):
                    if type(v) is not expected_type or v != expected_value:
                        raise ValueError(f"Expected exactly {expected_type.__name__}({expected_value}), got {type(v).__name__}({v})")
                    return v
                return validator
            
            # Use Annotated with BeforeValidator for strict type checking
            return Annotated[Literal[literal_value], BeforeValidator(create_strict_validator(literal_value, literal_type))]
        elif isinstance(ts_type, TS_Struct):
            # For a TypeScript object/struct, create nested Pydantic model
            fields = {}

            model_name = f"DynamicModel_{id(ts_type)}"

            # Raise an exception if recursion is detected
            if model_name in created_models:
                raise ValueError(f"Recursive type detected: {model_name}")

            for field_name, field_type in ts_type.obj.items():
                is_optional = field_name.endswith("?")
                actual_name = field_name.rstrip("?")

                field_pydantic_type = convert_type(
                    field_type,
                    required=not is_optional,
                )

                # Make non-required fields Optional
                if not required or is_optional:
                    field_pydantic_type = Optional[field_pydantic_type]

                fields[actual_name] = (
                    field_pydantic_type,
                    Field(...) if required and not is_optional else None,
                )

            # Create a dynamic Pydantic model
            model = create_model(
                model_name, **fields, __config__=ConfigDict(strict=True, extra="forbid")
            )
            created_models[model_name] = model
            return model
        elif isinstance(ts_type, TS_Array):
            element_type = convert_type(ts_type.type)
            return List[element_type]
        elif isinstance(ts_type, TS_Union):
            # For unions, create a Union of all possible types
            union_types = [convert_type(t) for t in ts_type.types]
            if len(union_types) == 1:
                return union_types[0]
            return Union[tuple(union_types)]
        # elif isinstance(ts_type, TS_Any):
        #     return Any
        # elif isinstance(ts_type, TS_Never):
        #     return Never
        else:
            raise ValueError("Unsupported type")

    root_model_type = convert_type(root_type.type)

    Validator = create_model(
        "Validator",
        value=(root_model_type, ...),
        __config__=ConfigDict(strict=True, extra="forbid"),
    )
    return Validator
