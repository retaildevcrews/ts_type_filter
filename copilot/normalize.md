Write python a function, `normalize(tree, defaults)`. The `tree` parameter
a dictionary whose keys map to primitive types or other trees of primitive and trees.
The `defaults` parameter is a dictionary mapping string `keys` to object templates
represented as dictionaries. Object templates specify primitive values for keys.

The function makes a deep copy of tree, replacing any dictionary that has a `name`
property with the merge of the default template with the name name and the keys
in the `tree`. The keys from the tree should take precedence.

Example:

tree = {
  name: "foo",
  "a": 1,
  "c": {
    name: "bar"
  }
}

defaults = {
  "foo": {"a": 123, "b": 2},
  "bar": {"x": "hello"}
}

Result of normalize(tree, default):

tree = {
  "name": "foo",
  "a": 1,
  "b": 2,
  "c": {
    "name": "bar"
    "x": "hello"
  }
}
