import pytest

from ts_type_filter import (
    Array,
    build_type_index,
    build_filtered_types,
    Define,
    Literal,
    ParamDef,
    ParamRef,
    Struct,
    Type,
    Union,
)


def filter(type_defs, query):
    symbols, indexer = build_type_index(type_defs)
    reachable = build_filtered_types(type_defs, symbols, indexer, query)
    lines = set(x.format() for x in reachable)
    return lines


def parse(expected):
    lines = [line.strip() for line in expected.strip().split("\n")]
    no_blanks = [l for l in lines if l]
    return set(no_blanks)


type_defs = [
    Define("Cart", [], Struct({"items": Array(Type("Item"))})),
    Define(
        "Item",
        [],
        Union(
            Type("J"),
            Type("P"),
            Type("Q", [ParamRef(Type("V"))]),
            Type("R", [ParamRef(Type("WXYZ"))]),
        ),
    ),
    Define(
        "P",
        [],
        Struct({"p1": Type("V"), "p2": Type("W"), "p3": Type("X"), "p4": Type("Y")}),
    ),
    Define("Q", [ParamDef("T")], Struct({"q1": Type("T")})),
    Define("R", [ParamDef("T", Type("WXYZ"))], Struct({"r1": Type("T")})),
    Define("WXYZ", [], Union(Type("W"), Type("X"), Type("Y"), Type("Z"))),
    Define("V", [], Literal("v")),
    Define("W", [], Literal("w")),
    Define("X", [], Literal("x")),
    Define("Y", [], Literal("y")),
    Define("Z", [], Literal("z")),
    Define("J", [], Type("K")),
    Define("K", [], Type("L")),
    Define("L", [], Union(Literal("l"), Literal("m"))),
]

test_cases = [
    (type_defs, "", "type Cart=never;", "no search term"),
    (type_defs, "bad", "type Cart=never;", "non existant search term"),
    (
        type_defs,
        "v w x y z",
        """
          type Cart={items:Item[]};
          type Item=P|Q<V>|R<WXYZ>;

          type P={p1:V,p2:W,p3:X,p4:Y};
          type Q<T>={q1:T};
          type R<T extends WXYZ>={r1:T};

          type WXYZ=W|X|Y|Z;
          type V="v";
          type W="w";
          type X="x";
          type Y="y";
          type Z="z";
        """,
        "all search terms",
    ),
    (
        type_defs,
        "v",
        """
          type Cart={items:Item[]};
          type Item=Q<V>;

          type Q<T>={q1:T};

          type V="v";
        """,
        "union1",
    ),
    (
        type_defs,
        "v w",
        """
            type Cart={items:Item[]};
            type Item=Q<V>|R<WXYZ>;
            type Q<T>={q1:T};
            type R<T extends WXYZ>={r1:T};
            type WXYZ="w";
            type V="v";
        """,
        "union2",
    ),
    (
        type_defs,
        "w x y z",
        """
            type Cart={items:Item[]};
            type Item=R<WXYZ>;
            type R<T extends WXYZ>={r1:T};
            type WXYZ=W|X|Y|Z;
            type W="w";
            type X="x";
            type Y="y";
            type Z="z";
        """,
        "struct1",
    ),
    (
        type_defs,
        "x y",
        """
            type Cart={items:Item[]};
            type Item=R<WXYZ>;
            type R<T extends WXYZ>={r1:T};
            type WXYZ=X|Y;
            type X="x";
            type Y="y";
        """,
        "struct2",
    ),
    (
        type_defs,
        "l",
        """
            type Cart={items:Item[]};
            type Item="l";
        """,
        "path collapse 1",
    ),
    (
        type_defs,
        "l m",
        """
            type Cart={items:Item[]};
            type Item="l"|"m";
        """,
        "path collapse 2",
    ),
    # TODO: subgraph.is_local(self.name)
    # TODO: hint comments
    # TODO: pinned
    # TODO: optionals - end with ?
]


@pytest.mark.parametrize(
    "type_defs, query, expected, test_name", test_cases, ids=[x[3] for x in test_cases]
)
def test_one_case(type_defs, query, expected, test_name):
    expected = parse(expected)
    observed = filter(type_defs, query)
    o = list(observed)
    o.sort()
    e = list(expected)
    e.sort()
    assert (
        observed == expected
    ), f"❌ Test Failed: {test_name} | Observed \n  {"\n  ".join(o)}\nExpected \n  {"\n  ".join(e)}"
