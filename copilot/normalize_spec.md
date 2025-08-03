The function create_normalizer_spec() in ts_type_filter/normalize.py has a limitation in that
is does not handle declarations of the form

~~~typescript
type GROUP = OPTION<"a" | "b">;

type OPTION<NAME> = {
  name: NAME;
  field1?: number;
  field2: string;
}
~~~

The GROUP declaration is never processed because it doesn't define a struct. I would like
to treat these sorts of declarations as if they were

~~~typescript
type GROUP = {
  name: "a" | "b";
  field1?: number;
  field2: string;
}
~~~

Please put test and debugging files in the copilot/normalize folder.