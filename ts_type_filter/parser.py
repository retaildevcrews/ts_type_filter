import ast

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

lines: (define | comment)*

define: "type" CNAME type_params? "=" type (";")?

type_params: "<" param_def ("," param_def)* ">"
param_def: CNAME ("extends" type)?

?type: union

?union: ("|")? intersection ("|" intersection)*
?intersection: array

array: primary array_suffix*
array_suffix: "[" "]"

?primary: literal
        | literalex
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

literalex: "LITERAL" "<" string_literal "," string_literal_list "," boolean_literal ">"
?string_literal_list: "[" (string_literal ("," string_literal)*)? "]"
?boolean_literal: TRUE | FALSE
TRUE: "true"
FALSE: "false"

literal: numeric_literal | string_literal
numeric_literal: SIGNED_NUMBER
string_literal: ESCAPED_STRING | ESCAPED_STRING2

comment: LINE_COMMENT | BLOCK_COMMENT
LINE_COMMENT: /\/\/[^\n]*/
BLOCK_COMMENT: /\/\*[\s\S]*?\*\//
ESCAPED_STRING2 : "'" _STRING_ESC_INNER "'"
%import common.CNAME
%import common.ESCAPED_STRING
%import common._STRING_ESC_INNER
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

# Lazy initialization of parser to avoid compilation cost at import time
_parser = None

def get_parser():
    global _parser
    if _parser is None:
        import lark
        _parser = lark.Lark(grammar, start="start")
    return _parser


def isToken(node, type_name):
    import lark
    return isinstance(node, lark.Token) and node.type == type_name



def parse(text):
    import lark
    
    # Create Transformer class dynamically to avoid import-time dependency
    # Transformer class converts the parse tree into AST nodes.
    class ParseTransformer(lark.Transformer):
        def lines(self, children):
            result = []
            for child in children:
                if isinstance(child, tuple):
                    comment_type, content = child
                    if comment_type == "line_hint":
                        result.append("//" + content)
                    elif comment_type == "block_hint":
                        result.append("/*" + content + "*/")
                # if isToken(child, "LINE_COMMENT"):
                #     if child.value.startswith("// Hint: "):
                #         result.append("//" + child[8:])
                # elif isToken(child, "BLOCK_COMMENT"):
                #     if child.value.startswith("/* Hint: "):
                #         result.append("/*" + child[8:])
                #     else:
                #         result.append(child.value)
                elif child is not None:
                    result.append(child)
            return result

        def define(self, children):
            # TODO: BUG: only preserves last comment
            hint = None
            while isToken(children[0], "COMMENT"):
                hint = children.pop(0).value[2:].strip()  # Strip `// ` from comment token

            name = children.pop(0).value  # Get the name of the type
            params = (
                children.pop(0) if type(children[0]) == list else []
            )  # Get type parameters if any
            value = children.pop()  # The type definition itself
            return Define(name, params, value, hint)

        def comment(self, items):
            # items[0] will be either a LINE_COMMENT or BLOCK_COMMENT token
            comment_token = items[0]
            
            if isToken(comment_token, "LINE_COMMENT"):
                if comment_token.value.startswith("// Hint: "):
                    # Extract the hint content after "// Hint: "
                    hint_content = comment_token.value[8:]  # Skip "// Hint: "
                    return ("line_hint", hint_content)
            elif isToken(comment_token, "BLOCK_COMMENT"):
                if comment_token.value.startswith("/* Hint: "):
                    # Extract the hint content, removing "/* Hint: " at start and "*/" at end
                    hint_content = comment_token.value[8:-2]  # Skip "/* Hint: " and "*/"
                    return ("block_hint", hint_content)

            # Skip non-hint comments by returning None
            return None

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
        
        def literalex(self, items):
            text = items.pop(0)
            temp = items.pop(0)
            aliases = [temp] if isinstance(temp, str) else temp.children
            pinned = True if items.pop(0) == "true" else False
            return Literal(text, aliases, pinned)

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
    
    parser = get_parser()
    tree = parser.parse(text)
    return ParseTransformer().transform(tree)
