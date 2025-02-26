import os
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ts_type_filter import (
    Array,
    build_type_index,
    build_filtered_types,
    Define,
    Literal,
    Struct,
    Type,
    Union,
)


###############################################################################
#
# Usage example
#
###############################################################################
def go():
    type_defs = [
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
    for x in type_defs:
        print(x.format())

    #
    # Print out filtered type definition
    #
    print("========================")

    symbols, indexer = build_type_index(type_defs)
    reachable = build_filtered_types(
        type_defs, symbols, indexer, "I'll have a ham sandwich with no tomatoes"
    )

    for n in reachable:
        print(n.format())


# TODO: modify build_filtered_types to take list of streams

go()
