from typing import Annotated, Any, Callable, List, Literal, Optional, Union

from ts_type_filter import (
    Any as TS_Any,
    Array as TS_Array,
    Define as TS_Define,
    Literal as TS_Literal,
    Node as TS_Node,
    Struct as TS_Struct,
    Union as TS_Union,
    Type as TS_Type,
)

Validator = Callable[[Any], bool]
Template = Callable[[List[Validator]], Validator]


def compile_node(
    ts_type: TS_Node,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    if isinstance(ts_type, TS_Array):
        return compile_array(ts_type, symbols, templates, locals)
    elif isinstance(ts_type, TS_Define):
        return compile_define(ts_type, symbols, templates, locals)
    elif isinstance(ts_type, TS_Literal):
        return compile_literal(ts_type, symbols, templates, locals)
    elif isinstance(ts_type, TS_Struct):
        return compile_struct(ts_type, symbols, templates, locals)
    elif isinstance(ts_type, TS_Type):
        return compile_type_ref(ts_type, symbols, templates, locals)
    elif isinstance(ts_type, TS_Union):
        return compile_union(ts_type, symbols, templates, locals)
    else:
        raise ValueError(f"Unsupported TS type: {ts_type}")


def compile_array(
    ts_array: TS_Array,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    element_template = compile_node(ts_array.type, symbols, templates, locals)

    def template(args: List[Validator]) -> Validator:
        element_validator = element_template(args)

        def validator(value: Any) -> bool:
            if not isinstance(value, list):
                return False
            for item in value:
                if not element_validator(item):
                    return False
            return True

        return validator

    return template


def compile_define(
    ts_define: TS_Define,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    if ts_define.name in templates:
        return templates[ts_define.name]

    def template(args: List[Validator]) -> Validator:
        if len(args) != len(ts_define.params):
            raise ValueError(
                f"Expected {len(ts_define.params)} arguments, got {len(args)}"
            )
        new_locals = {str(param.name): i for i, param in enumerate(ts_define.params)}
        inner_template = compile_node(ts_define.type, symbols, templates, new_locals)
        return inner_template(args)

    templates[ts_define.name] = template
    return template


def compile_literal(
    ts_literal: TS_Literal,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    def template(args: List[TS_Node]) -> Validator:
        def validator(value: Any) -> bool:
            return strict_equals(value, ts_literal.text)

        return validator

    return template


def compile_struct(
    ts_struct: TS_Struct,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    field_templates: dict[str, Template] = {}
    for field_name, field_type in ts_struct.obj.items():
        is_optional = field_name.endswith("?")
        actual_name = field_name.rstrip("?")

        field_templates[actual_name] = (
            is_optional,
            compile_node(field_type, symbols, templates, locals),
        )

    def template(args: List[Validator]) -> Validator:
        field_validators = {
            name: (is_optional, tmpl(args))
            for name, (is_optional, tmpl) in field_templates.items()
        }

        def validator(value: Any) -> bool:
            if not isinstance(value, dict):
                return False
            for field_name, (is_optional, field_validator) in field_validators.items():
                if field_name not in value:
                    if not is_optional:
                        return False
                elif not field_validator(value[field_name]):
                    return False

            # Check for extra fields in value
            for extra_field in value.keys():
                if extra_field not in field_validators:
                    return False
            return True

        return validator

    return template


def compile_type_ref(
    ts_type: TS_Type,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    type_def = symbols.get(ts_type.name)
    if type_def is not None:
        if len(ts_type.params or []) != len(type_def.params):
            raise ValueError(
                f"Expected {len(type_def.params)} arguments, got {len(ts_type.params)}"
            )

        inner_template = compile_define(type_def, symbols, templates, locals)
        params = ts_type.params or []
        arg_templates = [
            compile_node(param, symbols, templates, locals) for param in params
        ]

        def template(args: List[Validator]) -> Validator:
            validators = [arg_template(args) for arg_template in arg_templates]
            return inner_template(validators)

        return template

    index = locals.get(ts_type.name)
    if index is not None:

        def template(args: List[Validator]) -> Validator:
            if index >= len(args):
                raise ValueError(f"Type parameter index {index} out of range")
            return args[index]

        return template

    elif ts_type.name == "string":
        return primitive_type_template(str)
    elif ts_type.name == "number":
        # Special handling to exclude bool
        def template(args: List[Validator]) -> Validator:
            def validator(value: Any) -> bool:
                return type(value) in (int, float)

            return validator

        return template
    elif ts_type.name == "boolean":
        return primitive_type_template(bool)
    elif ts_type.name == "any":

        def template(args: List[Validator]) -> Validator:
            def validator(value: Any) -> bool:
                return True

            return validator

        return template
    elif ts_type.name == "never":

        def template(args: List[Validator]) -> Validator:
            def validator(value: Any) -> bool:
                return False

            return validator

        return template
    else:
        raise ValueError(f"Unknown type: {ts_type.name}")


def compile_union(
    ts_union: TS_Union,
    symbols: dict[str, TS_Define],
    templates: dict[str, Template],
    locals: dict[str, int],
) -> Template:
    templates = [
        compile_node(option, symbols, templates, locals) for option in ts_union.types]

    def template(args: List[Validator]) -> Validator:
        validators = [tmpl(args) for tmpl in templates]

        def validator(value: Any) -> bool:
            return any(v(value) for v in validators)

        return validator

    return template


def primitive_type_template(t) -> Template:
    def template(args: List[TS_Node]) -> Validator:
        def validator(value: Any) -> bool:
            types = t if t is tuple else (t,)
            return any(type(value) is x for x in types)

        return validator

    return template


def strict_equals(a, b):
    return a == b and type(a) is type(b)


def create_validator2(types: List[TS_Define], root_name: str) -> Validator:
    # Build symbol table for all type definitions
    bindings = {}
    for t in types:
        if isinstance(t, TS_Define):
            bindings[t.name] = t

    # Find the root type definition based on root_name
    root_type = bindings.get(root_name, None)
    if not root_type:
        raise ValueError(f"Root type '{root_name}' not found in type definitions")
    if len(root_type.params) != 0:
        raise ValueError("Root type must not have type parameters")

    templates = {}
    locals = {}
    root_template = compile_node(root_type, bindings, templates, locals)
    return root_template([])
