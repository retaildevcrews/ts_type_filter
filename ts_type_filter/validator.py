from pydantic import BaseModel, create_model, Field, field_validator, StringConstraints
import re
from typing import Annotated, Any, List, Optional, Union as PyUnion

from ts_type_filter.parser import Define, Struct, Union, Array, Type, Literal, Never
from ts_type_filter import Any as TSAny


def create_validator(types, root_name):
    # Build symbol table for all type definitions
    symbol_table = {}
    for t in types:
        if isinstance(t, Define):
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
        # Handle recursive types by tracking what we've seen
        if isinstance(ts_type, Type) and ts_type.name in created_models:
            return created_models[ts_type.name]

        if isinstance(ts_type, Struct):
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
            model = create_model(model_name, **fields)
            created_models[model_name] = model
            return model

        elif isinstance(ts_type, Array):
            # For arrays, create a List of the element type
            element_type = convert_type(ts_type.type)
            return List[element_type]

        elif isinstance(ts_type, Union):
            # For unions, create a Union of all possible types
            union_types = [convert_type(t) for t in ts_type.types]
            if len(union_types) == 1:
                return union_types[0]
            return PyUnion[tuple(union_types)]

        elif isinstance(ts_type, Type):
            # For named types, lookup the definition and convert it
            if ts_type.name in symbol_table:
                type_def = symbol_table[ts_type.name]
                if ts_type.name not in created_models:
                    model_type = convert_type(type_def.type)
                    created_models[ts_type.name] = model_type
                return created_models[ts_type.name]
            elif ts_type.name == "string":
                return str
            elif ts_type.name == "number":
                return float  # Using float for all numbers for simplicity
            elif ts_type.name == "boolean":
                return bool
            else:
                # For unknown types, fallback to Any
                return Any

        elif isinstance(ts_type, Literal):
            # For literals, create a pydantic model for a string with a constraint on the literal value
            # if isinstance(ts_type.text, str):
            pattern = r"^(" + "|".join(map(re.escape, [ts_type.text])) + r")$"
            return Annotated[str, StringConstraints(pattern=pattern)]

        elif ts_type is TSAny:
            # For the 'any' type, use Python's Any
            return Any

        elif isinstance(ts_type, Never):
            # For 'never' type, this is a type that can't be instantiated
            # We'll use None as a placeholder, though it's not a perfect analog
            return type(None)

        else:
            # Default case
            return Any

    # Create the root validator model
    root_model_type = convert_type(root_type.type)
    return root_model_type
