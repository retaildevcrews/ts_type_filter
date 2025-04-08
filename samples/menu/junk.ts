type Cart = { items: Item[] };

type Item =
  | WiseguyMeal<ComboSizes>
  | Meal<ComboSizes>
  | Wiseguy
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
  name: LITERAL<
    "Twofer Combo",
    ["pick choose two combination meal deal"],
    false
  >;
  one: TwoThreeChoices;
  two: TwoThreeChoices;
};

type ComboThree = {
  name: LITERAL<
    "Threefer Combo",
    ["pick choose three combination meal deal"],
    false
  >;
  one: TwoThreeChoices;
  two: TwoThreeChoices;
  three: TwoThreeChoices;
};

type TwoThreeChoices =
  | Wiseguy
  | GenericChicken<"Grilled Chicken Sandwich">
  | GenericBurger<LITERAL<"Bacon Cheeseburger", ["buger"], false>>
  | FrenchFries<LITERAL<"Medium", [], true>>
  | OtherFries<
      LITERAL<"Jalapeño Poppers", [], true>,
      LITERAL<"6 Piece", [], true>
    >
  | FountainDrink<
      | LITERAL<"Coca-Cola", ["coca", "cola", "coke"], false>
      | LITERAL<"Diet Coke", ["coca", "cola"], false>
      | LITERAL<"Dr. Pepper", ["doctor"], false>
      | "Sprite",
      LITERAL<"Medium", [], true>
    >
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
    | LITERAL<"Regular", [], true>
    | "With Bacon"
    | "With Cheese"
    | "With Bacon and Cheese"
    | CHOOSE;
  options?: Veggies | Sauces;
};

type PattyMelt = {
  name:
    | LITERAL<"Hero Melt", ["patty"], false>
    | LITERAL<"Bacon Melt", ["patty"], false>
    | LITERAL<"Mushroom and Swiss Melt", ["shroom", "patty"], false>;
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

type Chicken = GenericChicken<
  | "Grilled Chicken Sandwich"
  | LITERAL<"Cordon Bleu", ["chicken sandwich blue"], false>
>;

type GenericChicken<NAME> = {
  name: NAME;
  options?: (Veggies | Bacon | GenericCheese<"American Cheese"> | Condiments)[];
};

type KoreanChicken = {
  name:
    | LITERAL<"Sweet and Spicy Chicken", ["Korean fried sandwich"], false>
    | LITERAL<"Seasame Soy Chicken", ["Korean fried sandwich"], false>
    | LITERAL<"Spicy Garlic Chicken", ["Korean fried sandwich"], false>;
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
  name: LITERAL<
    "Captain Nemo Burger",
    ["white fish cod scrod sandwich"],
    false
  >;
  options?: (Veggies | Bacon | Cheeses | Condiments | Preparations | Extras)[];
};

type FrenchFries<SIZE extends FrenchFrySizes> = {
  name: "French Fries" | "Onion Rings" | "Sweet Potato Fries";
  size: SIZE;
};

type FrenchFrySizes = "Value" | "Small" | "Medium" | "Large" | CHOOSE;

type OtherFries<
  NAME extends "Jalapeño Poppers" | "Mozzarella Sticks",
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
  | LITERAL<"Coca-Cola", ["coca", "cola", "coke"], false>
  | LITERAL<"Diet Coke", ["coca", "cola"], false>
  | LITERAL<"Coca-Cola Zero Sugar", ["coca", "cola", "coke", "diet"], false>
  | LITERAL<"Dr. Pepper", ["doctor"], false>
  | "Dr. Pepper"
  | "Root Beer"
  | "Diet Root Beer"
  | "Sprite"
  | "Sprite Zero"
  | "Sweetened Tea"
  | "Unsweetened Tea"
  | "Strawberry Lemonade"
  | LITERAL<"Arnold Palmer", ["iced tea lemonade"], false>
  | LITERAL<"Powerade Zero", "Gatoraid", false>;

type Ice = { name: "Ice"; amount: "Regular" | "Light" | "No" };

type Veggies = {
  amount: ExtraAmount;
  name: "Lettuce" | "Tomato" | "Onion" | "Pickles" | "Jalapeños";
};

type Cheeses = GenericCheese<
  "American Cheese" | "Cheddar Cheese" | "Swiss Cheese"
>;

type GenericCheese<NAME> = { name: NAME; amount: Optional };

type Bacon = { amount: Optional; name: "Bacon" };

type Condiments = {
  amount: Amount;
  name:
    | "Ketchup"
    | "Mustard"
    | LITERAL<"Mayo", ["mayonnaise", "hellmanns"], false>
    | LITERAL<"BBQ", ["barbecue"], false>;
};

type Sauces = { amount: Amount; name: "Smokey Sauce" | "Green Goddess Sauce" };

type DippingSauce = {
  name:
    | LITERAL<"BBQ Dipping Sauce", ["barbecue"], false>
    | "Buffalo Dipping Sauce"
    | "Cool Ranch Dipping Sauce"
    | "Honey Mustard Dipping Sauce"
    | "Nacho Dipping Sauce"
    | "None";
};

type Extras = { amount: ExtraAmount; name: "Onion Rings" | "Jalapeños" };

type Preparations = {
  amount: Optional;
  name: "Cut in Half" | "Plain" | "Low Carb";
};

type Amounts = Amount | ExtraAmount | Optional;

type Amount = "No" | "Light" | LITERAL<"Regular", [], true> | "Extra";

type ExtraAmount = "No" | LITERAL<"Regular", [], true> | "extra";

type Optional = "No" | LITERAL<"Regular", [], true>;

// Hint: Use CHOOSE when customer doesn't specify an option
type CHOOSE = LITERAL<"CHOOSE", [], true>;

type LITERAL<NAME, ALIASES, IS_OPTIONAL> = NAME;
