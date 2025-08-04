
type GROUPS = GROUP1 | GROUP2;
type GROUP1 = OPTION<"a" | "b">;
type GROUP2 = BOOLEANOPTION<"c" | "d">;

type OPTION<NAME> = {
  name: NAME;
  field1?: number;
  field2: string;
}

type BOOLEANOPTION<NAME> = {
  name: NAME;
}

/* Expect output as if Typescript were

type GROUP1 = {
  name: "a" | "b";
  field1?: number;
  field2: string;
}
  
type GROUP2 = {
  name: "c" | "d";
}

*/
