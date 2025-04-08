import ast
import lark

from ts_type_filter import (
    Any,
    Array,
    Define,
    Literal,
    Never,
    ParamDef,
    Struct,
    Type,
    Union,
)

grammar = r"""
?start: lines

lines: (define | COMMENT)*

define: "type" CNAME type_params? "=" type (";")?

type_params: "<" param_def ("," param_def)* ">"
param_def: CNAME ("extends" type)?

?type: union

?union: ("|")? intersection ("|" intersection)*
?intersection: array

array: primary array_suffix*
array_suffix: "[" "]"

?primary: literal
        | "never"         -> never
        | "any"           -> any
        | type_ref
        | struct
        | "(" type ")"

type_ref: CNAME type_args?
type_args: "<" type ("," type)* ">"

struct: "{" [field (("," | ";") field)*] ("," | ";")? "}"
field: CNAME QUESTION? ":" type
QUESTION: "?"

literal: numeric_literal | string_literal
numeric_literal: SIGNED_NUMBER
string_literal: ESCAPED_STRING | ESCAPED_STRING2

COMMENT: /\/\/[^\n]*/
ESCAPED_STRING2 : "'" _STRING_ESC_INNER "'"
%import common.CNAME
%import common.ESCAPED_STRING
%import common._STRING_ESC_INNER
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

parser = lark.Lark(grammar, start="start")


def isToken(node, type_name):
    return isinstance(node, lark.Token) and node.type == type_name


# Transformer class that turns parse tree into AST nodes
class Transformer(lark.Transformer):
    def lines(self, children):
        result = []
        for child in children:
            if isToken(child, "COMMENT"):
                if child.value.startswith("// Hint: "):
                    result.append("//" + child[8:])
            else:
                result.append(child)
        return result

    def define(self, children):
        hint = None
        while isToken(children[0], "COMMENT"):
            hint = children.pop(0).value[2:].strip()  # Strip `// ` from comment token

        name = children.pop(0).value  # Get the name of the type
        params = (
            children.pop(0) if type(children[0]) == list else []
        )  # Get type parameters if any
        value = children.pop()  # The type definition itself
        return Define(name, params, value, hint)

    def type_params(self, items):
        return items

    def param_def(self, items):
        name = items[0]
        extends = items[1] if len(items) > 1 else None
        return ParamDef(name, extends)

    def type_ref(self, items):
        name = items[0].value
        params = items[1] if len(items) > 1 else None
        return Type(name, params)

    def type_args(self, items):
        return items

    def array(self, items):
        result = items[0]
        for _ in range(len(items) - 1):
            result = Array(result)
        return result

    def struct(self, items):
        return Struct(dict(items))

    def field(self, items):
        name = items.pop(0).value
        if isToken(items[0], "QUESTION"):
            name = name + "?"
            items.pop(0)
        value = items.pop(0)
        return [name, value]

    def pair(self, items):
        return (items[0].value, items[1])

    def literal(self, items):
        return Literal(items[0])

    def string_literal(self, items):
        return ast.literal_eval(items[0])

    def numeric_literal(self, items):
        try:
            return int(items[0])
        except ValueError:
            return float(items[0])

    def never(self, _):
        return Never()

    def any(self, _):
        return Any

    def union(self, items):
        if len(items) == 1:
            return items[0]
        return Union(*items)


def parse(text):
    tree = parser.parse(text)
    return Transformer().transform(tree)
