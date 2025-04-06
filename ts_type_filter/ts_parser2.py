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
?start: define

define: COMMENT? "type" CNAME type_params? "=" type ";"

comment: COMMENT

type_params: "<" param_def ("," param_def)* ">"
param_def: CNAME ("extends" type)?

?type: union

?union: intersection ("|" intersection)*
?intersection: array

?array: primary ("[" "]")?

?primary: literal
        | "never"         -> never
        | type_ref
        | struct
        | "(" type ")"

type_ref: CNAME type_args?
type_args: "<" type ("," type)* ">"

struct: "{" [pair ("," pair)*] "}"
pair: CNAME ":" type

literal: ESCAPED_STRING

COMMENT: /\/\/[^\n]*/
%import common.CNAME
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""


# # Load grammar from string or file
# with open("ts_type_filter/typescript.lark") as f:
#     grammar = f.read()

parser = Lark(grammar, start="start")


# Transformer class that turns parse tree into AST nodes
class ToAST(Transformer):
    def define(self, items):
        i = 0
        hint = None
        if isinstance(items[i], Token) and items[i].type == 'COMMENT':
            hint = items[i].value[2:].strip()  # Strip `// ` from comment token
            i += 1
        name = items[i].value
        i += 1
        params = []
        if i < len(items) - 1:
            params = items[i]
            i += 1
        value = items[i]
        # hint = items[0].value[2:].strip() if isinstance(items[0], str) else None
        # name = items[1].value if hint else items[0].value
        # # name = items[1].value if hint else items[0].children[0].value
        # params = items[2] if hint else items[1]
        # type_ = items[3] if hint else items[2]
        return Define(name, params, value, hint)

    # def define(self, items):
    #     if isinstance(items[0], Tree) and items[0].data == "comment":
    #         hint = items[0].children[0][2:].strip()  # Strip `// ` from comment token
    #         name = items[1].value
    #         params = items[2] if isinstance(items[2], list) else []
    #         type_ = items[3]
    #     else:
    #         hint = None
    #         name = items[0].value
    #         params = items[1] if isinstance(items[1], list) else []
    #         type_ = items[2]

    #     return Define(name, params, type_, hint)
    
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
        return Literal(json.loads(items[0]))

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
