from abc import ABC, abstractmethod
from collections import OrderedDict
import json

from inverted_index import Index

def extractor(node):
    text = []
    if isinstance(node, Literal):
        text.append(node.text)
        if node.aliases:
            text.append(node.aliases)
    return text
    
class TypeIndex:
    def __init__(self):
        self._index = Index(extractor)
        pass

    def add(self, node, terms):
        self._index.add(node)

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

    def keep(self, node):
        return node in self._nodes
    
    def original(self, key):
        return self._symbols.get(key)

    def filtered(self, key):
        return self._filtered.get(key)

    def add(self, key, type):
        if key in self._filtered:
            raise ValueError(f"Key {key} already exists in the graph.")
        self._filtered[key] = type


def build_symbol_table(nodes):
    symbols = SymbolTable()
    for node in nodes:
        if isinstance(node, Define):
            symbols.add(node.name, node)
    return symbols


class Node(ABC):
    next_id = 0

    def __init__(self):
        self.id = Node.next_id
        Node.next_id += 1

    @abstractmethod
    def format(self):
        pass

    @abstractmethod
    def index(self, graph, indexer):
        pass

    @abstractmethod
    def filter(self, nodes):
        pass

    @abstractmethod
    def visit(self, subgraph, visitor):
        pass


class Define(Node):
    def __init__(self, name, params, type):
        self.name = name
        self.params = params
        self.type = type

    def format(self):
        params = (
            f"<{",".join([p.format() for p in self.params])}>"
            if len(self.params or []) > 0
            else ""
        )
        return f"type {self.name}{params}={self.type.format()};"

    def index(self, graph, indexer):
        for param in self.params:
            param.index(graph, indexer)
        self.type.index(graph, indexer)

    def filter(self, nodes):
        # TODO: do we filter type parameters?
        t = self.type.filter(nodes)
        return Define(self.name, self.params, t)
    
    def visit(self, subgraph, visitor):
        # print(f"visit: {self.format()}")
        visitor(self)
        for p in self.params:
            p.visit(subgraph, visitor)
        self.type.visit(subgraph, visitor)


class Never(Node):
    def __init__(self):
        pass

    def format(self):
        return "never"

    def index(self, graph, indexer):
        pass

    def filter(self, nodes):
        return self
    
    def visit(self, subgraph, visitor):
        visitor(self)
        pass


class Param(Node):
    def __init__(self, name, extends=None):
        self.name = name
        self.extends = extends

    def format(self):
        return self.name + (f" extends {self.extends}" if self.extends else "")

    def index(self, graph, indexer):
        if self.extends:
            self.extends.index(graph, indexer)

    # TODO: do we filter extends logic?
    def filter(self, nodes):
        return self
    
    def visit(self, subgraph, visitor):
        visitor(self)
        if self.extends:
            self.extends.visit(subgraph, visitor)


class Union(Node):
    def __init__(self, *types):
        self.types = types

    def format(self):
        return "|".join([t.format() for t in self.types])

    def index(self, graph, indexer):
        for type in self.types:
            type.index(graph, indexer)

    def filter(self, nodes):
        types = [t.filter(nodes) for t in self.types]
        filtered = [t for t in types if not isinstance(t, Never)]
        if len(filtered) > 0:
            return Union(*filtered)
        return Never()
    
    def visit(self, subgraph, visitor):
        visitor(self)
        for t in self.types:
            t.visit(subgraph, visitor)


class Literal(Node):
    def __init__(self, text, aliases=None):
        self.text = text
        self.aliases = aliases

    def format(self):
        return json.dumps(self.text)

    def index(self, graph, indexer):
        indexer.add(self, self.text)
        if self.aliases:
            for alias in self.aliases:
                indexer(self, alias)

    def filter(self, subgraph):
        return self if subgraph.keep(self) else Never()
    
    def visit(self, subgraph, visitor):
        visitor(self)


class Struct(Node):
    def __init__(self, obj):
        self.obj = obj

    def format(self):
        return "{" + ",".join(f'"{k}":{v.format()}' for k, v in self.obj.items()) + "}"

    def index(self, graph, indexer):
        for k, v in self.obj.items():
            v.index(graph, indexer)

    def filter(self, subgraph):
        obj = {k: v.filter(subgraph) for k, v in self.obj.items()}
        filtered = {k: v for k, v in obj.items() if not isinstance(v, Never)}
        return Struct(filtered) if len(filtered) > 0 else Never()
    
    def visit(self, subgraph, visitor):
        visitor(self)
        for k, v in self.obj.items():
            v.visit(subgraph, visitor)


class Type(Node):
    def __init__(self, name, params=None):
        self.name = name
        self.params = params

    def format(self):
        return self.name + (
            f"<{",".join([p.format() for p in self.params])}>" if self.params else ""
        )

    def index(self, graph, indexer):
        pass

    def filter(self, subgraph):
        # TODO: type chain collapsing / path compression, e.g.
        #   type Drinks = Juice
        #   type Juice = {"name": "apple"}
        # becomes
        #   type Drinks = {"name": "apple"}
        filtered = subgraph.filtered(self.name)
        if not filtered:
            type = subgraph.original(self.name)
            filtered = type.filter(subgraph)
            subgraph.add(self.name, filtered)
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


class Array(Node):
    def __init__(self, type):
        self.type = type

    def format(self):
        return self.type.format() + "[]"

    def index(self, graph, indexer):
        self.type.index(graph, indexer)

    def filter(self, nodes):
        t = self.type.filter(nodes)
        return Array(t) if not isinstance(t, Never) else Never()
    
    def visit(self, subgraph, visitor):
        visitor(self)
        self.type.visit(subgraph, visitor)


###############################################################################
#
# Usage example
#
###############################################################################
def go():
    # a = Literal("abc")
    # print(a.format())
    # b = Array(Type("Node", [Param("A", 1), Param("B")]))
    # print(b.format())
    # c = Struct({"a": a, "b": b})
    # print(c.format())
    # d = Union(a, b, c)
    # print(d.format())
    # e = Define("Items", [Param("X", 1), Param("Y", 2)], d)
    # print(e.format())
    root = [
        Define("Items", [], Union(Type("Sandwiches"), Type("Drinks"))),
        Define(
            "Sandwiches",
            [],
            Struct(
                {
                    "name": Union(Literal("Ham Sandwich"), Literal("Turkey Sandwich")),
                    "options": Array(Type("SandwichOptions")),
                }
            ),
        ),
        Define(
            "SandwichOptions",
            [],
            Struct(
                {
                    "name": Union(
                        Literal("lettuce"), Literal("tomato"), Literal("onion")
                    ),
                    "amount": Union(
                        Literal("no"), Literal("regular"), Literal("extra")
                    ),
                }
            ),
        ),
        Define("Drinks", [], Union(Type("Soda"), Type("Juice"))),
        Define("Soda", [], Struct({"name": Union(Literal("Coke"), Literal("Pepsi"))})),
        Define(
            "Juice", [], Struct({"name": Union(Literal("Apple"), Literal("Orange"))})
        ),
    ]

    #
    # Print out original type definition
    #
    for x in root:
        print(x.format())

    #
    # Build the symbol table of defined types
    #
    print("========================")
    g = build_symbol_table(root)
    # g.print()

    #
    # Build index of terms mentioned in types
    #
    indexer = TypeIndex()
    for x in root:
        x.index(g, indexer)
    # print([x.format() for x in indexer.nodes("dummy")])

    #
    # Filter the graph based on search terms
    #
    nodes = indexer.nodes("apple ham tomato")
    subgraph = Subgraph(g, nodes)
    filtered = [n.filter(subgraph) for n in root]

    #
    # Collect nodes reachable from the root
    #
    reachable = OrderedDict()
    def visitor(node):
        if isinstance(node, Define):
            # print(f"add: {node.format()}")
            reachable[node] = None
            # filtered2.add(node)
            # for n in filtered2:
            #     print(f"  {n.format()}")

    filtered[0].visit(subgraph, visitor)

    # filtered = [n.filter(subgraph) for n in root]
    # filtered2 = [
    #     n for n in filtered if not (isinstance(n, Define) and isinstance(n.type, Never))
    # ]

    print('-----------------------')
    for n in reachable:
        print(n.format())


go()
