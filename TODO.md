# TODO

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