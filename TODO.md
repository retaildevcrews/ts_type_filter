# TODO

* Unit tests
* build_Filtered_types() should take list of text streams
* Referencing type parameters
* Path compression
  * Example
    * type A = B
    * type B = C
  * Example
    * type A<B extends C> = {x: B}
    * type C = "one_literal"
    * Could become type A = {x: "one_literal"}
* Optional struct members
* Some way to stop filtering so that Cart cannot be never?
* Comment parameter for types
* Better minification (e.g. newlines)
* Some means of pretty printing
* Some minimal type checking
  * Redefined type
  * Dangling reference
  * Never referenced
* Scenario - defaults
  * Defaults may not be mentioned by customer, causing filtering
  * Choose
* Scenario
    * type A<B extends C> = {x: B}
    * type C = never
    * Should collapse to never

