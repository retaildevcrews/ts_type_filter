# Pruning Algorithm Notes

The goal of the pruning algoritihm is to create a new, smaller type definition that preserves that semanics of the orgiginal type definition for scenarios involving a subset terms from string literal types.

## Initial Algorithm

* Given a sequence of query terms, mark each string literal type that matches one or more query terms.
* Convert other string literal types to type `never`.
* Flow the `never` types up the tree, performing transformation such as
  * A | never => never
  * {a: X, b: never} => never
  * A<never> => never
  * type A<X extends never> => never
* Prune all top-level declarations not reachable from root type.

This approach had challenges with certain scenarios.

### Challenge 0: LLM Hint Comments

Hint<TYPE, COMMENT>

### Challenge 1: query contains synonyms of terms in string literals

Consider the following type, representing a drink at a fast food restuarent:

~~~typescript
type Drinks = {
  name: "root beer" | "coca cola";
  size: "small" | "medium" | "large";
}
~~~

The query, "a value sized coke" will cause type `Drinks` to collapse to `never` because none of the three terms appear in any of the string literal types.

One solution is to provide a means to inform the pruning algoritm of aliases to be considered when marking string literal types. In an AST-like data structure the aliases could be provided in an additional node property. In Typescript source it could be provided by a special, built-in generic like LITERAL<TYPE, ALIASES>:

~~~typescript
type Drinks = {
  name: "root beer" | LITERAL<"coca cola", ["coke"]>;
  size: LITERAL<"small", ["value"]> | "medium" | "large";
}
~~~

### Challenge 2: query doesn't fully specify type.

Consider the following type representing a combo meal at a fast food restaurant:

~~~typescript
type ComboMeal = {
  name: "combo meal";
  sandwich: Bugers;
  drink: Drinks;
}

type Burgers = "hamburger" | "cheeseburger";
type Drinks = "root beer" | "diet root beer";
~~~

If the query is "a cheeseburger combo" we'll get

~~~typescript
type Burgers = "cheeseburger";
type Drinks = never;
~~~

which will result in `ComboMeal` collapsing to

~~~typescript
type ComboMeal = never;
~~~

The solution here is to introduce a string literal type that represents a missing choice.

~~~typescript
type ComboMeal = {
  name: "combo meal";
  sandwich: Bugers | CHOOSE;
  drink: Drinks | CHOOSE;
}

type Burgers = "hamburger" | "cheeseburger";
type Drinks = "root beer" | "diet root beer";
type CHOOSE = "CHOOSE";
~~~

We can ensure that the CHOOSE type is never filtered, say, by adding "CHOOSE" to the query.
The query, ""a cheeseburger combo CHOOSE" now yields

~~~typescript
type ComboMeal = {
  name: "combo meal";
  sandwich: Bugers | CHOOSE;
  drink: CHOOSE;
}

type Burgers = "cheeseburger";
type CHOOSE = "CHOOSE";
~~~

While we can prevent type CHOOSE from collapsing by adding "CHOOSE" to the set of query terms, a better approach is to introduce the concept of "pinning", where certain nodes can be marked, declaratively, as never collapsing. If the types are represented as an AST-like data structure, the pinned status can be specified with an additional property. In TypeScript source code, pinning could be specified with a special, built-in generic, such as `Pinned<T>`.

~~~typescript
type CHOOSE = Pinned<"CHOOSE">;
~~~

### Challenge 3

With the query "choose 3", `FrenchFries<"Medium">` is included in `TwoThreeChoices` because 

* In `TwoThreeChoices` union, `FrenchFries<"Medium">`, the "Medium" literal is pinned.
* `FrenchFries.name` union includes `CHOOSE`, which is pinned.
* `FrenchFries.size` type is generic type parameter, and therefore not considered in pruning.

These definitions were needed so that the query "choose 3 onion rings" would work without mentioning `Medium`. The combo will only allow `SIZE="Medium` but the query should not requre the term `medium`.

Questions:

* Should `FrenchFries.name` include `CHOOSE`? How would the LLM have information to hint to the user that they need to choose from the three types of fries, when these are filtered? Actually, how would `FrenchFries` even remain in the type system if there wasn't a `CHOOSE` and the query didn't mention terms that could identify the type of fries?
* Are pure generic types (those that don't reference other types) filtered out or included? No. Since all type references are local, there should be no filtering. Verified with `GenericTest<NAME, SIZE>`
* Do type parameter references impact filtering? No. In Type.filter(self) there is a check whether `self.name` is local. Locals are defined in `Subgraph` methods `push()`, `pop()`, and `is_local()`.
* Do `extend` clauses in type parameters definitions impact filtering? Yes. See `Define.filter()`.
* Do types passed as generic parameters impact filtering? Yes. See `Type.filter()` and `ParamRef.filter()`.

Observation:

CHANGED DEFINITION to fix following behavior:
`PattyMelt` is never pruned, even for an empty query because `PattyMelt.name` includes `CHOOSE` and `PattyMelt.optional` is optional.

~~~typescript
type TwoThreeChoices =
  | Wiseguy
  | GenericChicken<"Grilled Chicken Sandwich">
  | GenericBurger<"Bacon Cheeseburger">
  | FrenchFries<"Medium">
  | GenericOtherFries<"Jalapeno Popper", "8 Piece">
  | OtherFries<"8 Piece">
  | GenericFountainDrink<
      "Coca-Cola" | "Diet Coke" | "Dr. Pepper" | "Sprite",
      "Medium"
    >
  | CHOOSE;

// TODO: extends FrenchFrySizes?
type FrenchFries<SIZE> = {
  name: "French Fries" | "Onion Rings" | "Sweet Potato Fries" | CHOOSE;
  size: SIZE;
};

type FrenchFrySizes = "Value" | "Small" | "Medium" | "Large" | CHOOSE;

type OtherFries<SIZE extends OtherFriesSizes> = {
  name: "Jalapeno Poppers" | "Mozzarella Sticks";
  size: SIZE;
};

type GenericOtherFries<NAME, SIZE extends OtherFriesSizes> = {
  name: NAME;
  size: SIZE;
};
~~~

## Menu Design Notes

### Use of pinned types

It is often useful to define a type to denote a choice that must be made.
In the following we use the type `CHOOSE` for this purpose.
Note that the type literal `"CHOOSE"` has been pinned so that it will never be pruned.
Since `"CHOOSE"` is pinned, it won't interfere with queries containing the term `"choose"`.
These queries will never filter the pinned type and they will never filter other
types that match `"choose"`.

In the definition of type `FrenchFries`, we don't include `CHOOSE` in the `name` union
because we want use the name field to control pruning.

~~~python
    Define(
        "FrenchFries",
        [ParamDef("SIZE", Type("FrenchFrySizes"))],
        Struct(
            {
                "name": Union(
                    Literal("French Fries"),
                    Literal("Onion Rings"),
                    Literal("Sweet Potato Fries"),
                    # Here CHOOSE is not required because
                    # the type FrenchFries has no field
                    # field specific to unnamed french fries.
                    # Type("CHOOSE"),
                ),
                "size": Type("SIZE"),
            }
        ),
    ),
    Define(
        "FrenchFrySizes",
        [],
        Union(
            Literal("Value"),
            Literal("Small"),
            Literal("Medium"),
            Literal("Large"),
            # Here CHOOSE is appropriate since it is reasonalbe
            # for one to reason about FrenchFries without
            # choosing a size.
            Type("CHOOSE"),
        ),
    ),
    Define(
        "CHOOSE",
        [],
        Literal("CHOOSE", [], True),
        "Use CHOOSE when customer doesn't specify an option",
    ),
~~~

The rationale for not including `CHOOSE` in the name `union` is that there is no
circumstance where we would want

~~~typescript
{
  name: CHOOSE;
  size: CHOOSE;
}
~~~

Contrast this with a case where the query terms select a class with a choice:

~~~typescript
type Cheese = {
  name: "cheese";
  type: "American" | "Cheddar" | CHOOSE;
}
~~~

Here is is totally reasonable to create an unspecified `Cheese`:

~~~typescript
{
  name: "cheese";
  type: CHOOSE;
}