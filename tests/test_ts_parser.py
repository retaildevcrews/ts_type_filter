import pytest

from ts_type_filter.ts_parser2 import parse_ts

test_cases = [
    # ignoring whitespace
    # single and double quotes
    # do we actually need tests for never, True, False, null?
    # consider one comprehensive test
    # why are tests so slow - is parser rebuilt for each test?
    ("type a=never;", "never"),
    ("type a<A,B,C>=never;", "type params"),
]

@pytest.mark.parametrize(
    "source, test_name", test_cases, ids=[x[1] for x in test_cases]
)
def test_one_case(source, test_name):
    tree = parse_ts(source)
    text = tree.format()
    assert(source == text), f"❌ Test Failed: {test_name} | Observed \n{text}\nExpected \n{source}"

