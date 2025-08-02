Define a python function create_defaults(type_defs) that returns a data structure that
can be used to specify default values for structs.

The data structure should have two dicts. The first dict maps from each string literal that is a legal value for a name field in a struct to the name of the struct's type. So, for example, if we had

type Foo = {
  name: "a" | "b";
  field1?: 1;
  field2?: 3;
}

type Bar = {
  name: "c";
  field3: "hello";
  field4?: 123;
}

the dict would be

{
  "a" : "Foo",
  "b" : "Foo",
  "c" : "Bar"
}

Assume that all string literals in `name` fields are unique.

The second dict mapes type names like "Foo" and "Bar" to dictionaries that contain
keys for each of the optional field. The values of these keys are `None`. So for the example above, the dict would be

{
  "Foo": {"field1": None, "field2": None},
  "Bar": {"field4": None}
}

Note that the type of the `name` field may be a union, or a reference to another type name. This algorthm should find all of the legal string literals for a name.

If should also detect name string literals that are duplicated across different struct types.
