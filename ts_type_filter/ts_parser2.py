import ast
from lark import Lark, Transformer, Token, Tree, v_args
import json
import os
import sys

# Add the parent directory to the sys.path so that we can import from the
# gotaglio package, as if it had been installed.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ts_type_filter import (
    Any,
    Array,
    build_type_index,
    build_filtered_types,
    Define,
    Literal,
    Never,
    ParamDef,
    ParamRef,
    Struct,
    Type,
    Union,
)

grammar = r"""
?start: lines

lines: (define | COMMENT)*

define: COMMENT* "type" CNAME type_params? "=" type ";"

type_params: "<" param_def ("," param_def)* ">"
param_def: CNAME ("extends" type)?

?type: union

?union: intersection ("|" intersection)*
?intersection: array

array: primary array_suffix*
array_suffix: "[" "]"

?primary: literal
        | "never"         -> never
        | type_ref
        | struct
        | "(" type ")"

type_ref: CNAME type_args?
type_args: "<" type ("," type)* ">"

struct: "{" [pair ("," pair)*] "}"
pair: CNAME ":" type

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

parser = Lark(grammar, start="start")

def isToken(node, type_name):
    return isinstance(node, Token) and node.type == type_name


# Transformer class that turns parse tree into AST nodes
class ToAST(Transformer):
    def lines(self, children):
        return [x for x in children if isinstance(x, Define)]  # Filter out comments and keep only Define nodes

    def define(self, children):
        hint = None
        while isToken(children[0], 'COMMENT'):
            hint = children.pop(0).value[2:].strip()  # Strip `// ` from comment token

        name = children.pop(0).value  # Get the name of the type
        params = children.pop(0) if type(children[0]) == list else []  # Get type parameters if any
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
        if len(items) == 2:
            return Array(items[0])
        return items[0]

    def struct(self, items):
        return Struct(dict(items))

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

    def union(self, items):
        if len(items) == 1:
            return items[0]
        return Union(*items)


# Example usage
def parse_ts(text):
    tree = parser.parse(text)
    return ToAST().transform(tree)


# Example
if __name__ == "__main__":
#     ts = """// some comment
# type Result<T extends string> = { status: "ok" | "fail", data: T[] };"""
    ts = '// comment\ntype A = "hi";'
    node = parse_ts(ts)
    print(node.format())
