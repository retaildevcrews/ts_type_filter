from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import List, Optional

from gotaglio.shared import to_json_string

from .inverted_index import Index


def extractor(node):
    text = []
    if isinstance(node, Literal):
        text.append(node.text)
        if node.aliases:
            text.extend(node.aliases)
    return text


class TypeIndex:
    def __init__(self):
        self._index = Index(extractor)
        pass

    def add(self, node):
        self._index.add(node)
        # TODO: BUGBUG: why doesn't this if-statement raise an exception
        # when node doesn't have a pinned attribute?
        # I think the answer is only Literal.index() calls this method.
        if node.pinned:
            self._index.pin(node)

    def nodes(self, terms):
        matches = self._index.match(terms)
        return matches


class SymbolTable:
    def __init__(self):
        self.nodes = {}

    def add(self, key, type):
        if key in self.nodes:
            raise ValueError(f"Key {key} already exists in the graph.")
        self.nodes[key] = type

    def get(self, key):
        value = self.nodes.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in the graph.")
        return value

    def print(self):
        for key, type in self.nodes.items():
            print(f"{key}: {type.format()}")


class Subgraph:
    def __init__(self, symbols, nodes):
        self._symbols = symbols
        self._nodes = set(nodes)
        self._filtered = {}
        self._context = []

    def keep(self, node):
        return node in self._nodes

    # is_local(), push(), and pop() are for handling type parameters.
    def is_local(self, key):
        for symbols in self._context:
            if key in symbols:
                return True
        return False

    def original(self, key):
        return self._symbols.get(key)

    def filtered(self, key):
        return self._filtered.get(key)

    def add(self, key, type):
        if key in self._filtered:
            raise ValueError(f"Key {key} already exists in the graph.")
        self._filtered[key] = type

    def push(self, symbols):
        self._context.append(symbols)

    def pop(self):
        self._context.pop()

    def process(self, name):
        filtered = self.filtered(name)
        if not filtered:
            type = self.original(name)
            filtered = type.filter(self)
            self.add(name, filtered)
        return filtered


class Node(ABC):
    next_id = 0

    def __init__(self):
        self.id = Node.next_id
        Node.next_id += 1

    @abstractmethod
    def format(self) -> str:
        pass

    @abstractmethod
    def index(self, symbols, indexer):
        pass

    @abstractmethod
    def filter(self, subgraph) -> "Node":
        pass

    @abstractmethod
    def visit(self, subgraph, visitor):
        pass


class AnyNode(Node):
    def __init__(self, pinned=True):
        pass

    def format(self):
        return "any"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


Any = AnyNode()


class FalseNode(Node):
    def __init__(self, pinned=True):
        pass

    def format(self):
        return "false"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


FalseValue = FalseNode()


class TrueNode(Node):
    def __init__(self, pinned=True):
        pass

    def format(self):
        return "true"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


TrueValue = TrueNode()


class StringNode(Node):
    def __init__(self, pinned=True):
        pass

    def format(self):
        return "string"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


String = StringNode()


class NumberNode(Node):
    def __init__(self, pinned=True):
        pass

    def format(self):
        return "number"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


Number = NumberNode()


class BooleanNode(Node):
    def __init__(self, pinned=True):
        pass

    def format(self):
        return "boolean"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


Boolean = BooleanNode()


class Array(Node):
    def __init__(self, type):
        self.type = type

    def format(self):
        if isinstance(self.type, Union):
            return f"({self.type.format()})[]"
        else:
            return self.type.format() + "[]"

    def index(self, symbols, indexer):
        self.type.index(symbols, indexer)

    def filter(self, subgraph):
        t = self.type.filter(subgraph)
        return Array(t) if not isinstance(t, Never) else Never()

    def visit(self, subgraph, visitor):
        visitor(self)
        self.type.visit(subgraph, visitor)


class ParamDef(Node):
    def __init__(self, name, extends=None):
        self.name = name
        self.extends = extends

    def format(self):
        return self.name + (f" extends {self.extends.format()}" if self.extends else "")

    def index(self, symbols, indexer):
        if self.extends:
            self.extends.index(symbols, indexer)

    # TODO: do we filter extends logic?
    def filter(self, subgraph):
        if self.extends:
            t = self.extends.filter(subgraph)
            if isinstance(t, Never):
                return ParamDef(self.name, Never())
            return ParamDef(self.name, t)
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        if self.extends:
            self.extends.visit(subgraph, visitor)


class Define(Node):
    def __init__(self, name, params: List[ParamDef], type, hint=None):
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

    def index(self, symbols, indexer):
        for param in self.params:
            param.index(symbols, indexer)
        self.type.index(symbols, indexer)

    def filter(self, subgraph):
        filtered_params = [p.filter(subgraph) for p in self.params]
        if any(p.extends and isinstance(p.extends, Never) for p in filtered_params):
            return Define(self.name, filtered_params, Never(), self.hint)

        context = [p.name for p in self.params]
        if len(context) > 0:
            subgraph.push(context)
        t = self.type.filter(subgraph)
        if len(self.params) == 0:
            while t and isinstance(t, Type):
                if t.params and len(t.params) > 0:
                    break
                t = subgraph.filtered(t.name).type

        if len(context) > 0:
            subgraph.pop()
        return Define(self.name, filtered_params, t, self.hint)

    def visit(self, subgraph, visitor):
        visitor(self)
        for p in self.params:
            p.visit(subgraph, visitor)
        self.type.visit(subgraph, visitor)


class Literal(Node):
    def __init__(self, text, aliases=None, pinned=False):
        self.text = text
        self.aliases = aliases
        self.pinned = pinned

    def format(self):
        return to_json_string(self.text)

    def index(self, symbols, indexer):
        # Literal can be string, number, or boolean. Only index strings.
        if isinstance(self.text, str):
            indexer.add(self)

    def filter(self, subgraph):
        return self if subgraph.keep(self) else Never()

    def visit(self, subgraph, visitor):
        visitor(self)


class Never(Node):
    def __init__(self):
        pass

    def format(self):
        return "never"

    def index(self, symbols, indexer):
        pass

    def filter(self, subgraph):
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        pass


class ParamRef(Node):
    def __init__(self, type):
        self.type = type

    def format(self):
        return self.type.format()

    def index(self, symbols, indexer):
        self.type.index(symbols, indexer)

    # TODO: do we filter extends logic?
    def filter(self, subgraph):
        # TODO: code like in Type
        type = self.type.filter(subgraph)
        if isinstance(type, Never):
            return Never()
        return self

    def visit(self, subgraph, visitor):
        visitor(self)
        if not isinstance(self.type, Never):
            self.type.visit(subgraph, visitor)


class Struct(Node):
    def __init__(self, obj):
        self.obj = obj

    def format(self):
        return "{" + ",".join(f"{k}:{v.format()}" for k, v in self.obj.items()) + "}"

    def index(self, symbols, indexer):
        for k, v in self.obj.items():
            v.index(symbols, indexer)

    def filter(self, subgraph):
        obj = {k: v.filter(subgraph) for k, v in self.obj.items()}
        requiredNevers = 0
        filtered = {}
        for k, v in obj.items():
            if isinstance(v, Never):
                if not k.endswith("?"):
                    requiredNevers += 1
            else:
                filtered[k] = v
        return Struct(filtered) if requiredNevers == 0 else Never()

    def visit(self, subgraph, visitor):
        visitor(self)
        for k, v in self.obj.items():
            v.visit(subgraph, visitor)


class Type(Node):
    def __init__(self, name, params: Optional[List['Node']] = None):
        self.name = name
        self.params = params

    def format(self):
        return self.name + (
            f"<{",".join([p.format() for p in self.params])}>" if self.params else ""
        )

    def index(self, symbols, indexer):
        if self.params:
            for p in self.params:
                p.index(symbols, indexer)

    def filter(self, subgraph):
        if not subgraph.is_local(
            self.name
        ):  # TODO: BUGBUG: This doesn't seem right - should be name of Type of Type
            # TODO: BUGBUG: isn't it possible to have two instances of the same generic with different type parameters?
            if self.params:
                # type_parameters = [subgraph.process(x.name) for x in self.params]
                type_parameters = [x.filter(subgraph) for x in self.params]
                # TODO: BUGBUG: query="choose two coke fries" fails because FrenchFries<Medium> in TwoThreeChoices becomes Never.
                # QUESTION: should we be filtering on type parameters?
                # Don't wanter filter FrenchFries<Medium> to from TwoThreeChoices but do want to
                # filter GenericCheese from Cheeses. First example flows down. Second example
                # flows up.
                # Tried only filtering if 2 or more type parameters. Problem is there are both cases with one param.
                # TEMPORARY comment out below
                if any(
                    (isinstance(param, Define) and isinstance(param.type, Never))
                    or isinstance(param, Never)
                    for param in type_parameters
                ):
                    return Never()

            filtered = subgraph.process(self.name)
            if isinstance(filtered, Define) and isinstance(filtered.type, Never):
                return Never()

        return self

    def visit(self, subgraph, visitor):
        type = subgraph.filtered(self.name)
        if type:
            type.visit(subgraph, visitor)
        if self.params:
            for p in self.params:
                p.visit(subgraph, visitor)


class Union(Node):
    def __init__(self, *types):
        self.types = types

    def format(self):
        return "|".join([t.format() for t in self.types])

    def index(self, symbols, indexer):
        for type in self.types:
            type.index(symbols, indexer)

    def filter(self, subgraph):
        types = [t.filter(subgraph) for t in self.types]
        filtered = [t for t in types if not isinstance(t, Never)]
        if len(filtered) == 0:
            return Never()
        elif len(filtered) == 1:
            return filtered[0]
        else:
            return Union(*filtered)

    def visit(self, subgraph, visitor):
        visitor(self)
        for t in self.types:
            t.visit(subgraph, visitor)


#
# Builders
#
def build_symbol_table(nodes):
    symbols = SymbolTable()
    for node in nodes:
        if isinstance(node, Define):
            symbols.add(node.name, node)
    # TODO: BUGBUG: is this necessary?
    symbols.add("any", Any)
    symbols.add("false", FalseValue)
    symbols.add("true", TrueValue)
    # Add built-in TypeScript primitive types
    symbols.add("string", String)
    symbols.add("number", Number)
    symbols.add("boolean", Boolean)
    # Note: 'never' is already implemented as the Never class
    symbols.add("never", Never())
    return symbols


def build_type_index(type_defs):
    # Build the symbol table for type name references.
    symbols = build_symbol_table(type_defs)

    # Build index of terms mentioned in types.
    indexer = TypeIndex()
    for x in type_defs:
        # If x is not a comment
        if type(x) is not str:
            x.index(symbols, indexer)

    # TODO: BUGBUG: is this necessary?
    Any.index(symbols, indexer)
    
    # Index built-in types so they're searchable
    String.index(symbols, indexer)
    Number.index(symbols, indexer)
    Boolean.index(symbols, indexer)

    return symbols, indexer


def build_filtered_types(type_defs, symbols, indexer, text):
    # Filter the graph based on search terms
    nodes = indexer.nodes(text)
    subgraph = Subgraph(symbols, nodes)

    filtered = []
    for i, n in enumerate(type_defs):
        # If n is not a comment
        if type(n) is not str:
            f = n.filter(subgraph)
            filtered.append(f)
            # print(f"{i}:\n  {n.format()}\n  {f.format()}")

    # print()
    # print("+++ Filtered Types ++++++++++++")
    # for n in filtered:
    #     print(n.format())
    # print("+++++++++++++++")

    # Collect nodes reachable from the root
    reachable = OrderedDict()

    def visitor(node):
        if isinstance(node, Define):
            reachable[node] = None

    filtered[0].visit(subgraph, visitor)

    # NOTE that the nodes in reachable are in traversal order,
    # not source order.
    return reachable


def collect_string_literals(data):
    """
    Collects all string literal values in a hierarchical dictionary.

    Args:
      data (dict): The hierarchical dictionary to traverse.

    Returns:
      list: A list of all string literal values found in the dictionary.
    """
    literals = set()

    def _collect(data):
        if isinstance(data, dict):
            for key, value in data.items():
                _collect(value)
        elif isinstance(data, list):
            for item in data:
                _collect(item)
        elif isinstance(data, str):
            literals.add(data)

    _collect(data)
    return [x for x in literals]
