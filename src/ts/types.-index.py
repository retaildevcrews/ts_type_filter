from abc import ABC, abstractmethod
import json

class Indexer:
    def __init__(self):
        self._nodes = set()
        pass

    def add(self, node, terms):
        if "Ham" in terms:
            self._nodes.add(node)
        if "lettuce" in terms:
            self._nodes.add(node)
        print(node.format())
        print(f"  {terms}")


    def nodes(self, terms):
        return self._nodes
        # nodes = set()
        # for term in terms:
        #     if term in self.nodes:
        #         nodes.add(self.nodes[term])
        # return [node]

class Graph:
    def __init__(self):
      self.nodes = {}

    def add(self, key, type):
      if key in self.nodes:
        raise ValueError(f"Key {key} already exists in the graph.")
      self.nodes[key] = type

    def print(self):
      for key, type in self.nodes.items():
        print(f"{key}: {type.format()}")

def build_graph(nodes):
    graph = Graph()
    for node in nodes:
        if isinstance(node, Define):
            graph.add(node.name, node)
    return graph

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

class Never(Node):
    def __init__(self):
        pass

    def format(self):
        return "never"

    def index(self, graph, indexer):
        pass

    def filter(self, nodes):
        return self

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

    def filter(self, nodes):
        return self if self in nodes else Never()


class Struct(Node):
    def __init__(self, obj):
        self.obj = obj

    def format(self):
        return "{" + ",".join(f'"{k}":{v.format()}' for k, v in self.obj.items()) + "}"

    def index(self, graph, indexer):
        for k, v in self.obj.items():
            v.index(graph, indexer)

    def filter(self, nodes):
        obj = {k: v.filter(nodes) for k, v in self.obj.items()}
        filtered = { k: v for k, v in obj.items() if not isinstance(v, Never) }
        return Struct(filtered) if len(filtered) > 0 else Never()


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

    def filter(self, nodes):
        return self


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
    for x in root:
        print(x.format())
    print("========================")
    g = build_graph(root)
    g.print()

    indexer = Indexer()
    
    for x in root:
        x.index(g, indexer)

    print([x.format() for x in indexer.nodes("dummy")])

    filtered = [n.filter(indexer.nodes("dummy")) for n in root]
    for n in filtered:
        print(n.format())

go()
