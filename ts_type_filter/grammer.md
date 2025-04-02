Help me write a parser in Lark for a subset of the TypeScript language relating
to type definitions. The parser should be able to parse constructs relating to
the following AST nodes.

~~~
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def format(self):
        pass


class Array(Node):
    def __init__(self, type):
        self.type = type

    def format(self):
        if isinstance(self.type, Union):
            return f"({self.type.format()})[]"
        else:
            return self.type.format() + "[]"


class Define(Node):
    """
    Represents a TypeScript type definition of the form

    // Optional hint comment
    type name<param1,param2,...>=some_type
    """
    def __init__(self, name, params, type, hint=None):
        self.name = name
        self.params = params
        self.type = type
        self.hint = hint

    def format(self):
        hint = f"// {self.hint}\n" if self.hint else ""
        params = (
            f"<{",".join([p.format() for p in self.params])}>"
            if len(self.params or []) > 0
            else ""
        )
        return f"{hint}type {self.name}{params}={self.type.format()};"



class Literal(Node):
    """
    Represents either a TypeScript string literal type like "home"
    or an instance of the LITERAL<text,aliases> type, like LITERAL<"home","address">.
    """
    def __init__(self, text, aliases=None, pinned=False):
        self.text = text
        self.aliases = aliases
        self.pinned = pinned

    def format(self):
        return json.dumps(self.text)


class Never(Node):
    """
    Represents the TypeScript type 'never'.
    """
    def __init__(self):
        pass

    def format(self):
        return "never"


class ParamDef(Node):
    """
    Represents a TypeScript type parameter definition of the form
    `A` or `A extends SOME_TYPE`
    """
    def __init__(self, name, extends=None):
        self.name = name
        self.extends = extends

    def format(self):
        return self.name + (f" extends {self.extends.format()}" if self.extends else "")


class ParamRef(Node):
    """
    Represents a TypeScript type parameter reference of the form `A`
    """
    def __init__(self, type):
        self.type = type

    def format(self):
        return self.type.format()


class Struct(Node):
    """
    Represents a TypeScript struct type of the form
    {
        field1: type,
        field2: type,
        ...
    }
    """
    def __init__(self, obj):
        self.obj = obj

    def format(self):
        return "{" + ",".join(f"{k}:{v.format()}" for k, v in self.obj.items()) + "}"


class Type(Node):
    """
    Represents an instance of TypeScript type of the form
    `SOME_TYPE` or `SOME_TYPE<param1,param2,...>`
    """
    def __init__(self, name, params=None):
        self.name = name
        self.params = params

    def format(self):
        return self.name + (
            f"<{",".join([p.format() for p in self.params])}>" if self.params else ""
        )


class Union(Node):
    """
    Represents a TypeScript union type of the form
    `SOME_TYPE | SOME_OTHER_TYPE`
    """
    def __init__(self, *types):
        self.types = types

    def format(self):
        return "|".join([t.format() for t in self.types])
~~~

# Answer

~~~
typescript.lark

?start: define

define: comment? "type" CNAME type_params? "=" type ";"

comment: COMMENT

type_params: "<" param_def ("," param_def)* ">"
param_def: CNAME ("extends" type)?

?type: union_type array_suffix?

union_type: primary_type ("|" primary_type)*

array_suffix: "[" "]"

?primary_type: literal
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
~~~

~~~python
from lark import Lark, Transformer, Tree
import json

from ts_ast import Define, ParamDef, Type, Struct, Literal, Array, Never, Union, ParamRef  # your classes here

with open("typescript.lark") as f:
    grammar = f.read()

parser = Lark(grammar, start="start")


class ToAST(Transformer):
    def define(self, items):
        if isinstance(items[0], Tree) and items[0].data == "comment":
            hint = items[0].children[0][2:].strip()
            name = items[1].value
            params = items[2] if isinstance(items[2], list) else []
            type_ = items[3]
        else:
            hint = None
            name = items[0].value
            params = items[1] if isinstance(items[1], list) else []
            type_ = items[2]

        return Define(name, params, type_, hint)

    def type_params(self, items):
        return items

    def param_def(self, items):
        name = items[0]
        extends = items[1] if len(items) > 1 else None
        return ParamDef(name, extends)

    def type(self, items):
        base = items[0]
        if len(items) > 1:
            return Array(base)
        return base

    def union_type(self, items):
        if len(items) == 1:
            return items[0]
        return Union(*items)

    def type_ref(self, items):
        name = items[0].value
        params = items[1] if len(items) > 1 else None
        return ParamRef(Type(name, params))

    def type_args(self, items):
        return items

    def struct(self, items):
        return Struct(dict(items))

    def pair(self, items):
        return (items[0].value, items[1])

    def literal(self, items):
        return Literal(json.loads(items[0]))

    def never(self, _):
        return Never()

    def comment(self, items):
        return Tree("comment", items)


# Usage example
def parse_ts(text):
    tree = parser.parse(text)
    return ToAST().transform(tree)


if __name__ == "__main__":
    ts = """// some comment
type Result<T extends string> = { status: "ok" | "fail", data: T[] };"""
    node = parse_ts(ts)
    print(node.format())

~~~
