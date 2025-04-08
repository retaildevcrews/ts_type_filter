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
  | OtherFries<"Jalapeño Poppers", "6 Piece">
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
  name: "Lettuce" | "Tomato" | "Onion" | "Pickles" | "Jalapeños";
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
type Extras = { amount: ExtraAmount; name: "Onion Rings" | "Jalapeños" };
type Preparations = {
  amount: Optional;
  name: "Cut in Half" | "Plain" | "Low Carb";
};
type Amounts = Amount | ExtraAmount | Optional;
type Amount = "No" | "Light" | "Regular" | "Extra";
type ExtraAmount = "No" | "Regular" | "extra";
type Optional = "No" | "Regular";
// Hint: Use CHOOSE when customer doesn't specify an option
type CHOOSE = "CHOOSE";
