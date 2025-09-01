from pydantic import (
    ConfigDict,
    create_model,
    Field,
    BeforeValidator,
)
from typing import Annotated, Any, List, Literal, Optional, Union

from ts_type_filter import (
    Array as TS_Array,
    Define as TS_Define,
    Literal as TS_Literal,
    Struct as TS_Struct,
    Union as TS_Union,
    Type as TS_Type,
)


class Symbols:
    def __init__(self, bindings: dict[str, Any], parent: Optional["Symbols"] = None):
        self._bindings = bindings
        self._parent = parent

    def get(self, name):
        if name in self._bindings:
            return self._bindings[name]
        if self._parent:
            return self._parent.get(name)
        return None


def create_validator(types, root_name):
    # Build symbol table for all type definitions
    bindings = {}
    for t in types:
        if isinstance(t, TS_Define):
            bindings[t.name] = t
    symbols = Symbols(bindings)

    # Find the root type definition based on root_name
    root_type = symbols.get(root_name)
    if not root_type:
        raise ValueError(
            f"Root type '{root_name}' not found in type definitions"
        )  # Keep track of models we've already created to avoid recursion issues

    model_cache = {}
    root_model_type = convert(model_cache, symbols, root_type.type, True)

    Validator = create_model(
        "Validator",
        value=(root_model_type, ...),
        __config__=ConfigDict(strict=True, extra="forbid"),
    )
    return Validator

    # type A = B<C,D>;
    # type B<X,Y>={x:X, y:Y};
    # type C=1;
    # type D='hello';


# Recursive function to convert TypeScript types to Pydantic types
def convert(model_cache: dict[str, Any], symbols: Symbols, ts_type, required):
    if isinstance(ts_type, TS_Type):
        return convert_type(model_cache, symbols, ts_type, required)
    elif isinstance(ts_type, TS_Literal):
        return convert_literal(model_cache, symbols, ts_type, required)
    elif isinstance(ts_type, TS_Struct):
        return convert_struct(model_cache, symbols, ts_type, required)
    elif isinstance(ts_type, TS_Array):
        element_type = convert(model_cache, symbols, ts_type.type, required)
        return List[element_type]
    elif isinstance(ts_type, TS_Union):
        # For unions, create a Union of all possible types
        union_types = [convert(model_cache, symbols, t, required) for t in ts_type.types]
        if len(union_types) == 1:
            return union_types[0]
        return Union[tuple(union_types)]
    else:
        raise ValueError("Unsupported type")


def convert_define(
    model_cache: dict[str, Any],
    symbols: Symbols,
    type_def: TS_Define,
    params,
    required,
):
    if type_def.params:
        # Create a dict of converted param types
        param_bindings = {}
        if params and len(params) == len(type_def.params):
            for param_def, param_ref in zip(type_def.params, params):
                param_type = symbols.get(param_ref.name).type
                param_bindings[param_def.name] = param_type
        else:
            raise ValueError("Parameter mismatch")

        # Create the validator for type_def in this context
        model_type = convert(
            model_cache, Symbols(param_bindings, symbols), type_def.type, required
        )

        return model_type
    else:
        if type_def.name not in model_cache:
            model_type = convert(model_cache, symbols, type_def.type, required)
            model_cache[type_def.name] = model_type
        return model_cache[type_def.name]


def convert_literal(
    model_cache: dict[str, Any], symbols: Symbols, ts_type: TS_Literal, required
):
    # Create a strict validator that checks exact type and value
    literal_value = ts_type.text
    literal_type = type(literal_value)

    def create_strict_validator(expected_value, expected_type):
        def validator(v):
            if type(v) is not expected_type or v != expected_value:
                raise ValueError(
                    f"Expected exactly {expected_type.__name__}({expected_value}), got {type(v).__name__}({v})"
                )
            return v

        return validator

    # Use Annotated with BeforeValidator for strict type checking
    return Annotated[
        Literal[literal_value],
        BeforeValidator(create_strict_validator(literal_value, literal_type)),
    ]


def convert_type(
    model_cache: dict[str, Any], symbols: Symbols, ts_type: TS_Type, required
):
    type_def = symbols.get(ts_type.name)
    if type_def:
        if isinstance(type_def, TS_Define):
            return convert_define(model_cache, symbols, type_def, ts_type.params, required)
        else:
            return convert(model_cache, symbols, type_def, required)
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


def convert_struct(
    model_cache: dict[str, Any], symbols: Symbols, ts_type: TS_Struct, required
):
    # For a TypeScript object/struct, create nested Pydantic model
    fields = {}

    model_name = f"DynamicModel_{id(ts_type)}"

    # Raise an exception if recursion is detected
    if model_name in model_cache:
        raise ValueError(f"Recursive type detected: {model_name}")

    for field_name, field_type in ts_type.obj.items():
        is_optional = field_name.endswith("?")
        actual_name = field_name.rstrip("?")

        field_pydantic_type = convert(
            model_cache,
            symbols,
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
    model_cache[model_name] = model
    return model
