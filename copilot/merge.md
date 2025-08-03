Create the python function merge_normalizer_specs(newSpec, originalSpec, renamedTypes) that merges two
normalizer specs that were produced by create_normalizer_spec().

* The merged spec should use the new `types` dictionary and discard the original `types` dictionary
* The merged `duplicates` dictionary should come from `newSpec`
* The merged `defaults` dictionary should be the merge of the original and new `defaults` dictionaries where
  * Newly introduced types not in the renamedTypes dictionary are added
  * Newly introduced types in the renamedTypes dictionary cause a rename in the orginal entry
  * Existing types are retained, along with their defaults. Renames should generate a warning on the list of warnings returned.
  * Original types, not mentioned in `newSpec`, are flagged as stale entries
  * Stale entries bound to None are removed.
  * Stale entries bound to a dict are retained with the warning.
* The return value should be a tuple containing the merged spec and a list of warnings relating to renames and stale entries
* The algorithm should look for duplicates and name collisions in the rename dictionary.

