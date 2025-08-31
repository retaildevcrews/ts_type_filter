from pydantic import (
    BaseModel,
    ConfigDict,
    create_model,
    Field,
    field_validator,
    StringConstraints,
)
from typing import Annotated, Any, List, Literal, Optional, Union

from ts_type_filter import (
    Array as TS_Array,
    Define as TS_Define,
    Literal as TS_Literal,
    Struct as TS_Struct,
    Union as TS_Union,
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

    # # types is a list of Node objects, each of which has a `name` parameter
    # # find type with matching root_name of None
    # root_type = next(
    #     (t for t in types if t.name == root_name), None
    # )
    # if not root_type:
    #     raise ValueError(f"Unknown root type: {root_name}")

    ts_type = root_type.type

    # Recursive function to convert TypeScript types to Pydantic types
    def convert_type(ts_type, required=True, path=""):
        if isinstance(ts_type, TS_Literal):
            return Literal[ts_type.text]
            # return Annotated[Literal[ts_type.text], Field(strict=True)]
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
        else:
            raise ValueError("Unsupported type")

    root_model_type = convert_type(root_type.type)

    Container = create_model(
        "Container",
        value=(root_model_type, ...),
        __config__=ConfigDict(strict=True, extra="forbid"),
    )
    return Container
