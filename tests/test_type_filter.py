import json
import pytest

from ts_type_filter import (
    Array,
    build_type_index,
    build_filtered_types,
    Define,
    Literal,
    Param,
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


# class TestDefine:
#     def test_keep_rhs(self):
#         type_defs = [Define("Root", [], Type("A")), Define("A", [], Literal("B"))]
#         observed = filter(type_defs, "B")
#         expected = set(['type Root=A;', 'type A="B";'])
#         assert observed == expected

#     def test_filter_rhs(self):
#         type_defs = [Define("Root", [], Type("A")), Define("A", [], Literal("B"))]
#         observed = filter(type_defs, "C")
#         expected = set(['type Root=never;'])
#         assert observed == expected

type_defs1 = [Define("Root", [], Type("A")), Define("A", [], Literal("B"))]
type_defs2 = [Define("Root", [], Type("A")), Define("A", [Param("B")], Literal("C"))]
type_defs3 = [
    Define("Root", [], Type("A")),
    Define("A", [Param("B", Type("D"))], Literal("C")),
    Define("D", [], Literal("E")),
]

type_defs4 = [
    Define("Root", [], Struct({"items": Array(Type("A"))})),
    Define("A", [], Union(Type("B"), Type("C"))),
    Define("B", [Param("D")], Struct({"name": Literal("")})),
    Define("C", [Param("E"), Type("F")], Struct({"name": Literal("")})),
]

type_defs5 = [
    Define("Cart", [], Struct({"items": Array(Type("Item"))})),
    Define(
        "Item",
        [],
        Union(Type("P"), Type("Q", [Param("V")]), Type("R", [Param("WXYZ")])),
    ),
    Define(
        "P",
        [],
        Struct({"p1": Type("V"), "p2": Type("W"), "p3": Type("X"), "p4": Type("Y")}),
    ),
    Define("Q", [Param("T")], Struct({"q1": Type("T")})),
    Define("R", [Param("T", Type("WXYZ"))], Struct({"r1": Type("T")})),
    Define("WXYZ", [], Union(Type("W"), Type("X"), Type("Y"), Type("Z"))),
    Define("V", [], Literal("v")),
    Define("W", [], Literal("w")),
    Define("X", [], Literal("x")),
    Define("Y", [], Literal("y")),
    Define("Z", [], Literal("z")),
]

# Test cases as (input, expected_output, test_name)
# test_cases = [
#     (type_defs1, "B", ["type Root=A;", 'type A="B";'], "keep A"),
#     (type_defs1, "C", ["type Root=never;"], "prune A"),
#     (type_defs2, "C", ["type Root=A;", 'type A<B>="C";'], "prune A"),
#     (type_defs2, "D", ["type Root=never;"], "prune A"),
#     (type_defs2, "B D", ["type Root=never;"], "prune A"),
#     (type_defs3, "E", ["type Root=never;"], "prune A"),
#     (type_defs3, "C E", [d.format() for d in type_defs3], "prune A"),
# ]
test_cases = [
    (type_defs5, "", "type Cart=never;", "no search term"),
    (type_defs5, "bad", "type Cart=never;", "non existant search term"),
    (
        type_defs5,
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
        # Test failes because `type Item=Q<V>` doesn't visit `V`.
        type_defs5,
        "v",
        """
          type Cart={items:Item[]};
          type Item=Q<V>;

          type Q<T>={q1:T};

          type V="v";
        """,
        "union1",
    ),
]


@pytest.mark.parametrize(
    "type_defs, query, expected, test_name", test_cases, ids=[x[3] for x in test_cases]
)
def test_square(type_defs, query, expected, test_name):
    expected = parse(expected)
    observed = filter(type_defs, query)
    o = list(observed)
    o.sort()
    e = list(expected)
    e.sort()
    assert (
        observed == expected
    ), f"❌ Test Failed: {test_name} | Observed \n  {"\n  ".join(o)}\nExpected \n  {"\n  ".join(e)}"
