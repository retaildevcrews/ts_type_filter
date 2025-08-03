Create the python function merge_normalizer_specs(newSpec, originalSpec, renamedTypes) that merges two
normalizer specs that were produced by create_normalizer_spec().

`newSpec` and `originalSpec` are normalizer specs.

A normalizer spec consists of three dictionaries
* `types`: maps item names to type names.
* `defaults`: maps type names to dictionaries that provide default values for certain fields.
* `duplicates`: provides information on situations where a single names was a candidate to be bound to multiple types. Since the `types` dictionary does not bind multiple types, `duplicates` just serves to report warnings about the normalizer spec generation process.

`renamedTypes` is a dictionary mapping old typenames to new typenames.

The user scenario is merge a `newSpec` with an `originalSpec`, while allowing for renames of types from the `originalSpec`.

* The merged spec should use the `types` and `duplicates` dictionaries from `newSpec`.
* The merge algorithm should first perform a deep copy of the `defaults` dictionary from `originalSpec`, renaming keys according to `renamedTypes`.
* It should then merge in the `defaults` dictionary from `newSpec`.
  * Entries with new keys should be added.
  * Entries that share a key with an existing entry should merge default values, with values from the new entry taking precedence over the values from the old entry.
* For keys that appear in the `defaults` dictionary from `originalSpec` but don't appear in `newSpec`
  * Generate a warning
  * Delete the entry if the default value is None or {}
* The algorithm should generate warnings for name collisions in `renamedTypes` where two keys map to the same typename.
* The algorithm should generate warnings for keys in the `renamedTypes` that don't appear in the `defaults` dictionary of `originalSpec`.
* The return value should be a tuple containing the merged spec and a list of warnings relating to renames and stale entries

Put the implmentation of `merge_normalizer_specs()` in `ts_type_filter/normalize.py`. Put test and debug code in the `copilot/merge` folder.