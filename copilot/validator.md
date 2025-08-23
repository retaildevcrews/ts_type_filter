Write a function create_validator(types) that takes a the type data structure 
that is the return value of the parse() function in ts_type_filter/parser.py and returns a Pydantic validator for a dict that is supposed to conform to the schema represented by `types`.

For now, put the function in ts_type_filter/validator.py, but put other temporary code assets in copilot/validator.

You can casually verify your code with tests in copilot/validator, but don't author the comprehensive pydantic suite yet. We will do this later.
