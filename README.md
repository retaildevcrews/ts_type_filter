# ts_type_filter

This is an experimental library to assist in preparing Typescript type definitions for use in Large Language Model (LLM) prompts.
We've seen from projects like [TypeChat](https://github.com/microsoft/TypeChat) that TypeScript type definitions are a good way to communicate the desired output schema in an LLM prompt.

In some scenarios, such as restaurant menus, the Typescript type definition may be long, and it may be desireable to work with a subset of the type definition that specifies only the types needed for the current term.

For instance, if the customer is ordering a drink it is not necessary to include the types related to sandwiches.

`ts_type_filter` provides a data structure that reprpesents a complex TypeScript type definition. It maintains an inverted index of the terms in the string type literals, and this index is used to prune the type definition, based on the current contents of the shopping cart and the customer's request. You can learn more about the inverted index [here](./documentation/inverted-index.md).

As an example, suppose we have a menu for a restaurant with a very small menu offering two sandwiches with some toppings, two sodas, and two juices:

~~~typescript
type Items = Sandwiches | Drinks;

type Sandwiches = {
  name: "Ham Sandwich" | "Turkey Sandwich";
  options: SandwichOptions[];
};

type SandwichOptions = {
  name: "lettuce" | "tomato" | "onion";
  amount: "no" | "regular" | "extra";
};

type Drinks = Soda | Juice;
type Soda = { name: "Coke" | "Pepsi" };
type Juice = { name: "Apple" | "Orange" };
~~~

[Tiktoken](https://tiktokenizer.vercel.app/) shows that this type definition uses 106 tokens.

If the user says something like, "I'll have a ham sandwich with no tomatoes", the menu could be filtered to something like

~~~typescript
type Items = Sandwiches;

type Sandwiches = {
  name: "Ham Sandwich" | "Turkey Sandwich";
  options: SandwichOptions[];
};

type SandwichOptions = { name: "tomato"; amount: "no" };
~~~

This filtered menu uses only 47 tokens. The potential savings due to filtering is much more signifant for a large menu.

## Using ts_type_filter

~~~
poetry add git+https://github.com/MikeHopcroft/ts_type_filter
~~~

TODO:
  * poetry or pip install
  * import
  * use api to build type
  * filter to generate source text

## Building ts_type_filter

1. Verify you have python version >=3.12. Note that 3.13 may not be supported yet.
1. `pip install poetry` outside of any virtual environment.
2. `git clone https://github.com/MikeHopcroft/ts_type_filter.git`
3. `cd ts_type_filter`
4. `python -m venv .venv`
5. `.venv\Scripts\activate`
6. `poetry install --no-root`

~~~bash
% gotag run menu samples\menu\cases2.json infer.model.name=perfect prepare.compress=True

% gotag format latest > junk\out3.md
~~~

## Samples

COMING SOON

## Documentation

* [Inverted Index](./documentation/inverted-index.md)
* [Type Pruning Algorithm](./documentation/algorithm.md)
