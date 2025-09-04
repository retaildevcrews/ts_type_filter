# TODO

Top Top Top

* Validator error messages
* Make Symbols in validator.py threadsafe
* Rework validator - are custom validators really necessary?
* Unit test hierarchy for validator

* Take new gotaglio from pypi.org
* Merge turns into main
* Normalizer
  * Fix unit test
  * Two modes - add default and remove default
  * Generate directly from Typescript
  * Document - rationale, usage
  * Add coffee drinks and syrups to menu
* Document TS commentting limitations and features (hint:)
* x Take new gotaglio from test.pypi.org
* x Rename menu_pipeline.py, menu2.ipynb
* x Take new gotaglio from github
  * Rework prepare
    * x Get previous cart from stages
    * x Get all messages
    * x Prune based on all messages and previous cart



* x Fix unit tests
* TODO: consider creating full conversation history for all preceding turns.

* x Take new gotaglio
  * x console.print(f"Complete menu tokens: TODO  ")

* Bug: Array<A|B|C> filters to never if A is never, but (A|B|C)[] works
* Normalizer
  * Bug: named types with no optional fields don't show up in defaults.
    * Is this really a bug or can the normalizer deal with it?
  * create_normalizer_spec()
  * create_normalizer()
  * merge_normalizer_specs()
    * Merge logic with renaming not quite right
* Pydantic
* Parse errors
  * x Comments inside definitions - decided not to allow - hard to know if comment refers to preceding or next type
  * x Comments to the right of text - decided not to allow
  *x  /* Comments */
  * Better parse error message with line number and column
  * x Type `never`
  * x Type `string`
  * x Type `number`
* Are string, number, boolean, never and any implemented with the same pattern?
  * Is any indexed?
  * Why use never() instead of an alias?
* x Incorporate nest_async into Gotaglio?
* prepare.menu path needs to be different in CLI than notebook.
* Cleanup
  * Move flatten_cases to gotaglio
  * x cases3.json, multi_turn_cases.json
  * gotag.md in samples/menu
  * Rename gotag and gotag.bat?
  * Rename simple.ipynb to api.ipynb?
  * gotag and gotag.bat access nonexistant ordering.py
  * to_ts.py
  * x Rename ordering2.py to ordering.py to menu_pipeline.py
  * x debug.py
  * X filter.py
  * x pipeline.ipynb - can we remove this?
  * x Rename ordering.ipynb to pipeline.ipynb
  * x put cases in data folder
  * x junk1.txt, junk2.txt, junk.js, junk2.ts
  * x cases.json, cases2.json
* Make sure README.md is clear
* Test a larger set of cases
* Failing case analysis
  * x 0e6 - ChooseDrink needs to be templated by SIZE
  * c47 step 0 - Picked illegal Cheeseburger - prompt comment?
  * x c47 step 1 - Drink size in twofer is restricted to Medium. Should not be CHOOSE.
  * x 7ee - bad test case - expected value wrong
* x Flattener should copy keywords
* x Step number breaks uuid shortener
* x Replace junk.ts with menu.ts
* x Where are tomato emojis coming from? From :tomato:. Fixed in gotaglio.
* x Modify ordering.py to load menu.ts
* x Modify ordering.py to generate sub-result for each turn
* x uuid.step id prefixing
* x ordering pipeline should get type defs from file
  * x filename should come from config

Top Top
* Compare of perfect and flakey shows all failures
* Formatting of pipeline.ipynb markdown in github.
* Verify CHOOSE pinning. Why do we get type DrinkSizes="CHOOSE" instead of CHOOSE?
* PRUNING challenge: "a wiseguy without tomatoes"
* x Why do definitions appear in different order than menu.py
  * They are in traveral order, not source order.
  * Putting them in source order would require passing an order field to each of the constructors. This is a fairly significant change for a modest benefit.
  * In debug.py, CHOOSE is the fifth definition
* x Implement LITERAL<text, pinned, aliases>
  * x Remove hack/workaround code
  * x Reevaluate indexing of `any`
* Hint comments really need to be part of Define so they are not filtered out
* Investigate snowball treatment of Jalapeños
* Don't emit semicolons after {}, []

Top
* Notebooks should have help accessing models.json and .credentials.json
* dev container
  * .venv is not activated for some reason
  * ./gotag is not on path
* Update engine requirement
* Notebook example
* Erase old files
* Test dev container in codespaces
* Update documentation
  * README instructions
  * Pointer to architecture document - samples/menu/algorithm.md
  * Pointer to index documents
  * Update menu.ts to use LITERAL<> and HINT<>
* Add comment field to cases and format()
* Can add-id put the uuids at the top?
* Encapsulate pruning code in convenience function
* Pydantic serializer
* TS type parser + equivalent LLM prompt
* TS types for HINT, LITERAL w/aliases, PIN
* Cafe menu
* Kids meal menu
* x Consistent capitalization in amounts
* x Modify index to take array of text
* x Formatter show extracted text

* POTENTIAL BUG
  * "twofer combo with root beer will filter out drink choices because root beer is not allowed
* DippingSauceFlavor
* Hint<TYPE, TEXT>, PIN<TYPE>, ALIAS<TYPE>
* Public and private variables in classes - consistent usage, accessors.
* Typecheck arity and type of generic type parameters. Example
  * Include GenericTest in Items without providing type parameters
* x build_Filtered_types() should take list of text streams
* x Pinned nodes / defaults
* x Hint/Comment parameter for types
* Optional struct members
* Should be able to mark members as default. They will never be filtered.
  * e.g. Regular
* Some way to stop filtering so that Cart cannot be never?
* Better minification (e.g. newlines)
* Some means of pretty printing
* Some minimal type checking
  * Redefined type
  * Dangling reference
  * Never referenced
* Scenario - defaults
  * Defaults may not be mentioned by customer, causing filtering
  * Choose
* . Unit tests
  * . type filtlering
    * subgraph.is_local(self.name)
  * collect string literals
  * inverted index
* . Referencing type parameters
* Path compression
  * x Example
    * x type A = B
    * x type B = C
  * Example
    * type A<B extends C> = {x: B}
    * type C = "one_literal"
    * Could become type A = {x: "one_literal"}
* Scenario
    * type A<B extends C> = {x: B}
    * type C = never
    * Should collapse to never

Path compression scenarios:

type Cart={items:Item[]};
type Item=Q<V>;
type Q<T>={q1:T};
type V="v";

becomes

type Cart={items:Item[]};
type Item={q1:"v"};

Another path compression: double cheeseburger meal cut in half
type Preparations={amount:Optional,name:"Cut in Half"};
type Optional="regular";