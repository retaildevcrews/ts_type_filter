import pytest

from ts_type_filter.ts_parser2 import parse_ts

test_cases = [
    # x multiline input
    # comments anywhere
    # x ignoring whitespace
    # x single and double quotes
    # do we actually need tests for never, True, False, null?
    # consider one comprehensive test
    # why are tests so slow - is parser rebuilt for each test?
    ("type a=never;", "type a=never;", "never"),
    ("type a<A,B,C>=never;", "type a<A,B,C>=never;", "param def"),
    ("type a<A,B,C>={a:A, b:B, c:C};", "type a<A,B,C>={a:A,b:B,c:C};", "param ref"),
    (" type   a < A,B, C > = never ; ", "type a<A,B,C>=never;", "ignoring whitespace"),
    ('type a="hello";', 'type a="hello";', "double quotes"),
    ("type a='hello';", 'type a="hello";', "single quotes"),
    ("type a=123;", 'type a=123;', "number"),
    (
        "// this is a comment\ntype a<A,B,C>=never;",
        "// this is a comment\ntype a<A,B,C>=never;",
        "single-line comment",
    ),
    (
        "// this is a comment\n// this is another comment\ntype a<A,B,C>=never;",
        "// this is another comment\ntype a<A,B,C>=never;",
        "multi-line comment",
    ),
    ("type D={a:1,b:'text'};", 'type D={a:1,b:"text"};', "struct"),
    ("type A=B[];", 'type A=B[];', "array"),
    ("type a<A,B,C>=D;\ntype D={a:1};", "type a<A,B,C>=D;\ntype D={a:1};", "multiple defines"),
]


@pytest.mark.parametrize(
    "source, expected, test_name", test_cases, ids=[x[2] for x in test_cases]
)
def test_one_case(source, expected, test_name):
    tree = parse_ts(source)
    observed = '\n'.join([node.format() for node in tree])
    assert (
        observed == expected
    ), f"❌ Test Failed: {test_name} | Observed \n{observed}\nExpected \n{expected}"
