import pytest

from ts_type_filter import parse

test_cases = [
    # x multiline input
    # comments anywhere
    # x ignoring whitespace
    # x single and double quotes
    # do we actually need tests for never, True, False, null?
    # consider one comprehensive test
    # why are tests so slow - is parser rebuilt for each test?
    # handle export?
    # handle optional structure fields
    # semicolon not required at end of type definition
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
    ("type D={a:1,b:'text'};", 'type D={a:1,b:"text"};', "struct1"),
    ("type D={a:1,b:'text',};", 'type D={a:1,b:"text"};', "struct2"),
    ("type D={a:1;b:'text';};", 'type D={a:1,b:"text"};', "struct3"),
    ("type D={a:1,b:'text';};", 'type D={a:1,b:"text"};', "struct4"),
    ("type D={a?:1};", 'type D={a:1,b:"text"};', "optional struct field"),
    ("type A=B[];", 'type A=B[];', "array"),
    ("type A=B[][];", 'type A=B[][];', "array2"),
    ("type A={a:1,b:2}[];", 'type A={a:1,b:2}[];', "array3"),
    ("type A=B|C;", 'type A=B|C;', "union"),
    ("type A=|B|C;", 'type A=B|C;', "leading union"),
    ("type a<A,B,C>=D;\ntype D={a:1};", "type a<A,B,C>=D;\ntype D={a:1};", "multiple defines"),
    # Operator precedence
    ("type A=B|C[];", 'type A=B|C[];', "operator precedence"),
    ("type A=(B|C)[];", 'type A=(B|C)[];', "parentheses"),
    # Parentheses
    # Complex cases - array, union, and nested types
    (
        "type Result<T extends string> = { status: 'ok' | 'fail', data: T[] };",
        'type Result<T extends string>={status:"ok"|"fail",data:T[]};',
        "complex type with array and union",
    ),
    (
        "type A = { a: number, b: string } | { c: boolean };",
        "type A={a:number,b:string}|{c:boolean};",
        "union of structs",
    ),
    (
        "type A = Array<{ a: number, b: string }>; // comment",
        "type A=Array<{a:number,b:string}>;",
        "array of structs with comment",
    ),
    (
        "// comment\n// another comment\ntype A = 'hi' | 'bye'; // trailing comment",
        '// another comment\ntype A="hi"|"bye";',
        "union with trailing comments",
    ),
]


@pytest.mark.parametrize(
    "source, expected, test_name", test_cases, ids=[x[2] for x in test_cases]
)
def test_one_case(source, expected, test_name):
    tree = parse(source)
    observed = '\n'.join([node.format() for node in tree])
    assert (
        observed == expected
    ), f"❌ Test Failed: {test_name} | Observed \n{observed}\nExpected \n{expected}"

comprehensive = """
type Cart = { items: Item[] };

type Item =
  | WiseguyMeal<ComboSizes>
  | Meal<ComboSizes>
  | PattyMelt
  | Burger
  | Chicken
  | KoreanChicken
  | Pitas
  | Fish
  | ComboTwo
  | ComboThree
  | FrenchFries<any>
  | OtherFries<any, any>
  | FountainDrink<any, any>;

type WiseguyMeal<SIZE extends ComboSizes> = {
  name: "Wiseguy Meal";
  size: SIZE;
  sandwich: Wiseguy | CHOOSE;
  fries: FrenchFries<SIZE> | CHOOSE;
  drink: ChooseDrink;
};

type Meal<SIZE extends ComboSizes> = {
  name: "Meal";
  size: SIZE;
  sandwich:
    | Wiseguy
    | PattyMelt
    | Burger
    | Chicken
    | KoreanChicken
    | Pitas
    | Fish
    | CHOOSE;
  fries: FrenchFries<SIZE> | CHOOSE;
  drink: ChooseDrink;
};

type ComboTwo = {
  name: "Twofer Combo";
  one: TwoThreeChoices;
  two: TwoThreeChoices;
};

type ComboThree = {
  name: "Threefer Combo";
  one: TwoThreeChoices;
  two: TwoThreeChoices;
  three: TwoThreeChoices;
};

type TwoThreeChoices =
  | Wiseguy
  | GenericChicken<"Grilled Chicken Sandwich">
  | GenericBurger<"Bacon Cheeseburger">
  | FrenchFries<"Medium">
  | OtherFries<"Jalapeno Poppers", "6 Piece">
  | FountainDrink<"Coca-Cola" | "Diet Coke" | "Dr. Pepper" | "Sprite", "Medium">
  | CHOOSE;

type Wiseguy = GenericWiseguy<
  | "Wiseguy"
  | "Vegan Wiseguy"
  | "Double Wiseguy"
  | "Triple Wiseguy"
  | "Down East Wiseguy"
>;

type GenericWiseguy<NAME> = {
  name: NAME;
  type:
    | "Regular"
    | "With Bacon"
    | "With Cheese"
    | "With Bacon and Cheese"
    | CHOOSE;
  options?: Veggies | Sauces;
};

type PattyMelt = {
  name: "Hero Melt" | "Bacon Melt" | "Mushroom and Swiss Melt";
  options?: (Veggies | Bacon | Cheeses | Sauces | Condiments)[];
};

type Burger = GenericBurger<
  | "Bacon Double Cheeseburger"
  | "Bacon Cheeseburger"
  | "Double Cheeseburger"
  | "Cheeseburger"
>;

type GenericBurger<NAME> = {
  name: NAME;
  options?: (
    | Veggies
    | Bacon
    | Cheeses
    | Sauces
    | Condiments
    | Preparations
    | Extras
  )[];
};

type Chicken = GenericChicken<"Grilled Chicken Sandwich" | "Cordon Bleu">;

type GenericChicken<NAME> = {
  name: NAME;
  options?: (Veggies | Bacon | GenericCheese<"American Cheese"> | Condiments)[];
};

type KoreanChicken = {
  name:
    | "Sweet and Spicy Chicken"
    | "Seasame Soy Chicken"
    | "Spicy Garlic Chicken";
  options?: (
    | Veggies
    | Bacon
    | Cheeses
    | Sauces
    | Condiments
    | Preparations
    | Extras
  )[];
};

type Pitas = {
  name: "Lemon Chicken Pita" | "Smokey Chicken Pita" | "Tangy Chicken Pita";
  options?: (Veggies | Bacon | Cheeses | Sauces | Condiments | Extras)[];
};

type Fish = {
  name: "Captain Nemo Burger";
  options?: (Veggies | Bacon | Cheeses | Condiments | Preparations | Extras)[];
};

type FrenchFries<SIZE extends FrenchFrySizes> = {
  name: "French Fries" | "Onion Rings" | "Sweet Potato Fries";
  size: SIZE;
};

type FrenchFrySizes = "Value" | "Small" | "Medium" | "Large" | CHOOSE;

type OtherFries<
  NAME extends "Jalapeno Poppers" | "Mozzarella Sticks",
  SIZE extends OtherFriesSizes
> = { name: NAME; size: SIZE; sauce: DippingSauce | CHOOSE };

type OtherFriesSizes = "6 Piece" | "12 Piece" | CHOOSE;

type ComboSizes = "Small" | "Medium" | "Large" | CHOOSE;

type ChooseDrink = FountainDrink<any, any> | CHOOSE;

type FountainDrink<NAME extends DrinkNames, SIZE extends DrinkSizes> = {
  name: NAME;
  size: SIZE;
  options?: Ice[];
};

type DrinkSizes = "Value" | "Small" | "Medium" | "Large" | CHOOSE;

type DrinkNames =
  | "Coca-Cola"
  | "Diet Coke"
  | "Coca-Cola Zero Sugar"
  | "Dr. Pepper"
  | "Root Beer"
  | "Diet Root Beer"
  | "Sprite"
  | "Sprite Zero"
  | "Sweetened Tea"
  | "Unsweetened Tea"
  | "Strawberry Lemonade"
  | "Arnold Palmer"
  | "Powerade Zero";

type Ice = { name: "Ice"; amount: "Regular" | "Light" | "No" };

type Veggies = {
  amount: ExtraAmount;
  name: "Lettuce" | "Tomato" | "Onion" | "Pickles" | "Jalape\u00f1os";
};

type Cheeses = GenericCheese<
  "American Cheese" | "Cheddar Cheese" | "Swiss Cheese"
>;

type GenericCheese<NAME> = { name: NAME; amount: Optional };

type Bacon = { amount: Optional; name: "Bacon" };

type Condiments = {
  amount: Amount;
  name: "Ketchup" | "Mustard" | "Mayo" | "BBQ";
};

type Sauces = { amount: Amount; name: "Smokey Sauce" | "Green Goddess Sauce" };

type DippingSauce = {
  name:
    | "BBQ Dipping Sauce"
    | "Buffalo Dipping Sauce"
    | "Cool Ranch Dipping Sauce"
    | "Honey Mustard Dipping Sauce"
    | "Nacho Dipping Sauce"
    | "None";
};

type Extras = { amount: ExtraAmount; name: "Onion Rings" | "Jalopenos" };

type Preparations = {
  amount: Optional;
  name: "Cut in Half" | "Plain" | "Low Carb";
};

type Amounts = Amount | ExtraAmount | Optional;

type Amount = "No" | "Light" | "Regular" | "Extra";

type ExtraAmount = "No" | "Regular" | "extra";

type Optional = "No" | "Regular";

// Use CHOOSE when customer doesn't specify an option
type CHOOSE = "CHOOSE";
"""

def test_comprehensive():
    tree = parse(comprehensive)
    observed = '\n'.join([node.format() for node in tree])
    assert (
        observed == comprehensive
    ), f"❌ Test Failed: comprehensive | Observed \n{observed}\nExpected \n{comprehensive}"
