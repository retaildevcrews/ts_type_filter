from glom import glom
import json
import os
from rich.console import Console
from rich.text import Text
import sys
from typing import Any

# Add the parent directory to the sys.path so that we can import from the
# gotaglio package, as if it had been installed.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from gotaglio.dag import Dag
from gotaglio.exceptions import ExceptionContext
from gotaglio.format import format_messages
from gotaglio.main import main
from gotaglio.pipeline_spec import (
    ColumnSpec,
    FormatterSpec,
    get_result,
    get_stages,
    get_turn,
    PipelineSpec,
    SummarizerSpec,
)
from gotaglio.pipeline import Internal, Prompt
from gotaglio.repair import Repair
from gotaglio.shared import build_template, to_json_string
from gotaglio.summarize import keywords_column
from gotaglio.tokenizer import tokenizer

from ts_type_filter import (
    collect_string_literals,
    build_type_index,
    build_filtered_types,
    parse,
)


###############################################################################
#
# Default configuration values
#
###############################################################################

# Default configuration values for each pipeline stage.
# The structure and interpretation of each configuration dict is
# dictated by the needs of corresponding pipeline stages.
#
# An instance of `Prompt` indicates that the value must be provided on
# the command line. In this case, the user would need to provide values
# for the following keys on the command line:
#   - prepare.template
#   - infer.model.name
#
# An instance of `Internal` indicates that the value is provided by the
# pipeline runtime. Using a value of `Internal` will prevent the
# corresponding key from being displayed in help messages.
#
# There is no requirement to define a configuration dict for each stage.
# It is the implementation of the pipeline that determines which stages
# require configuration dicts.
configuration = {
    "prepare": {
        "compress": False,
        "menu": "data/menu.ts",
        "prune": True,
        "template": Prompt("Template file for system message"),
        "template_text": Internal(),
    },
    "infer": {
        "model": {
            "name": Prompt("Model name to use for inference stage"),
            "settings": {
                "max_tokens": 800,
                "temperature": 0.7,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0,
            },
        }
    },
}


###############################################################################
#
# Stage Functions
#
###############################################################################
def stages(name, config, registry):
    """
    Defines the structure of a simple, linear pipeline with four stages:
      **prepare** - creates the system prompt and user messages for the model
      **infer** - invokes the model to generate a response
      **extract** - attempts to extract a numerical answer from the model response
      **assess** - compares the extracted answer to the expected answer

    Parameters:
      name (str): Name of the pipeline. Can be used for error message formatting. Unused in this example.
      config (dict): Dictionary that supplies configuration settings used by stages.
      registry (object): Registry object providing access to models.

    Returns:
      dag_spec (object): A DAG specification object representing the pipeline stages
      and their execution order.

    Pipeline Stages:
      - prepare: Assembles system, assistant, and user messages for the model.
      - infer: Invokes the model to generate a response based on prepared messages.
      - extract: Attempts to extract a numerical answer from the model response.
      - assess: Compares the extracted answer to the expected answer for evaluation.
    """
    # Read the contents of menu.ts into a string.
    # Use utf8 because of terms like "jalapeño".
    filename = glom(config, "prepare.menu")
    with open(filename, "r", encoding="utf-8") as file:
        menu_text = file.read()

    # Parse the TypeScript type definitions
    # By parsing here, we ensure that any errors in the typescript
    # parsing are caught before the stage functions are run.
    type_defs = parse(menu_text)
    symbols, indexer = build_type_index(type_defs)

    # Determine whether to work with a compressed or uncompressed menu.
    # DESIGN NOTE: using string compare in case parameter was passed on
    # the command line. The argparse module does not know anything about
    # the typing for pipeline.prepare.compress=True.
    compress = str(glom(config, "pipeline.prepare.compress", default="False")) == "True"

    # Determine the number of tokens in the uncompressed menu.
    # These will be displayed by the formatter.
    # This also compiles once for the entire suite.
    complete = serialize_menu(type_defs, compress)
    complete_tokens = len(tokenizer.encode(complete))

    # Compile the jinja2 template used in the `prepare` stage.
    # Store the template source in the `prepare.template_text` key.
    # By building the template here, we ensure that any errors in the template
    # compilation are caught before the stage functions are run.
    template = build_template(
        config,
        "prepare.template",
        "prepare.template_text",
    )

    # Instantiate the model for the `infer` stage.
    # By creating the model here, we ensure that any errors, such as a bad
    # model name or configuration issues, are caught before the stage functions
    # are run.
    model = registry.model(glom(config, "infer.model.name"))

    # Define the pipeline stage functions. Each stage function is a coroutine
    # that takes a context dictionary as an argument.
    #
    # context["case"] has the `case` data for the current case. Typically
    # this comes from the cases.json or cases.yamlfile specified as a parameter
    # to the `run` sub-command.
    #
    # context["stages"][name] has the return value for stage `name`. Note
    # that context["stages"][name] will only be defined if after the stage
    # has successfully run to conclusion without raising an exception.
    #
    # Note that a stage function will only be invoked if all of its previous or
    # input stages have completed with a return value.

    # Stage 1:Create the system and user messages
    async def prepare(context):
        case = context["case"]
        i = len(context["turns"]) - 1

        #
        # Prune the menu based on terms in the query and the cart
        # Generate the pruning query based on the user query and the cart.
        #

        # Get all of the string literals from all of the previous carts.
        carts = [case["cart"]] + [
            turn["stages"]["extract"] for turn in context["turns"][:-1]
        ]
        cart = carts[-1]
        # For now, just collect strings from most resent cart.
        cart_literals = collect_string_literals(cart)

        # Get all of the previous user queries.
        # When i == 0 add place holder for missing system message.
        previous = (
            [None]
            if i == 0
            else context["turns"][i - 1]["stages"]["prepare"]["messages"]
        )

        # Add the user query for the current turn.
        assistant = {"role": "assistant", "content": to_json_string(cart)}
        user = {"role": "user", "content": context["case"]["turns"][i]["query"]}
        messages = previous[1:] + [assistant, user]

        # Full pruning query is based on the previous user queries and string
        # literals found in previous carts.
        user_queries = [m["content"] for m in messages if m["role"] == "user"]
        full_query = user_queries + cart_literals

        # Prune the menu based on the full query.
        reachable = build_filtered_types(type_defs, symbols, indexer, full_query)
        pruned = (
            serialize_menu(reachable, compress)
            if str(config["prepare"]["prune"]) == "True"
            else serialize_menu(type_defs, compress)
        )

        # Create the system message, based on the pruned menu.
        system = {"role": "system", "content": await template({"menu": pruned})}

        return {
            "messages": [system] + messages,
            "full_query": full_query,
            "complete_tokens": complete_tokens,
        }

    # Stage 2: Invoke the model to generate a response
    async def infer(context):
        stages = get_stages(context)
        return await model.infer(stages["prepare"]["messages"], context)

    # Stage 3: Attempt to extract a numerical answer from the model response.
    # Note that this method will raise an exception if the response is not
    # a number.
    async def extract(context):
        stages = get_stages(context)
        with ExceptionContext(f"Extracting JSON from LLM response."):
            text = stages["infer"]

            # Strip off fenced code block markers, if present.
            marker = "```json\n"
            if text.startswith(marker):
                text = text[len(marker) :]
            text = text.strip("```")
            return json.loads(text)

    # Stage 4: Compare the model response to the expected answer.
    async def assess(context):
        stages = get_stages(context)
        turn = get_turn(context)
        repair = Repair("id", "options", [], ["name"], "name")
        repair.resetIds()
        observed = repair.addIds(stages["extract"]["items"])
        expected = repair.addIds(turn["expected"]["items"])
        return repair.diff(observed, expected)

    # Define the pipeline
    # The dictionary keys supply the names of the stages that make up the
    # pipeline. Stages will be executed in the order they are defined in the
    # dictionary.
    #
    # For more complex pipelines, you can use the
    # `dag_spec_from_linear()` function to create arbitrary
    # directed acyclic graphs (DAGs) of stages.
    stages = {
        "prepare": prepare,
        "infer": infer,
        "extract": extract,
        "assess": assess,
    }

    return Dag.from_linear(stages)


def serialize_menu(type_defs, compress=False):
    separator = "" if compress else "\n"
    return separator.join([x.format() for x in type_defs])


###############################################################################
#
# Summarizer extensions
#
###############################################################################
def cost_cell(result, turn_index):
    """
    For user-defined `cost` column in the summary report table.
    Provides contents and formatting for the cost cell for the summary table.
    """
    cost = get_stages(result, turn_index)["assess"]["cost"]
    cost_text = "" if cost == None else f"{cost:.2f}"
    return (
        Text(cost_text, style="bold green")
        if cost == 0
        else Text(cost_text, style="bold red")
    )


def user_cell(result, turn_index):
    """
    For user-defined `user` column in the summary report table.
    Provides contents and formatting for the user cell in the summary table.
    This cell displays the user input for the specified turn index.
    """
    return get_turn(result, turn_index)["query"]


###############################################################################
#
# Formatter extensions
#
###############################################################################
def format_turn(console: Console, turn_index, result: dict[str, Any]):
    stages = get_result(result)
    passed = passed_predicate(result)
    if passed:
        console.print(f"### Turn {turn_index + 1}: **PASSED**  ")
    else:
        cost = glom(stages, "stages.assess.cost", default=None)
        console.print(f"### Turn {turn_index + 1}: **FAILED:** (cost={cost})  ")
    console.print()

    input_tokens = sum(
        len(tokenizer.encode(message["content"]))
        for message in stages["stages"]["prepare"]["messages"]
    )
    complete_tokens = glom(stages, "stages.prepare.complete_tokens", default=None)
    console.print(f"Complete menu tokens: {complete_tokens}  ")
    console.print(
        f"Input tokens: {input_tokens} ({input_tokens/complete_tokens:.0%}), output tokens: {len(tokenizer.encode(stages['stages']['infer']))}  \n"
    )

    format_messages(
        console, stages["stages"]["prepare"]["messages"], collapse=["system"]
    )
    console.print("**assistant:**")
    console.print("```json")
    console.print(to_json_string(stages["stages"]["extract"]))
    console.print("```")
    console.print()

    if passed:
        console.print("**No repairs**")
    else:
        console.print("**expected:**")
        console.print("<details><summary>Click to expand</summary>  \n")
        console.print("```json")
        console.print(to_json_string(result["case"]["turns"][turn_index]["expected"]))
        console.print("```")
        console.print("\n</details>  \n  \n")
        console.print("")
        console.print("**Repairs:**")
        for step in stages["stages"]["assess"]["steps"]:
            console.print(f"* {step}")

    console.print()
    console.print("**Pruning query**:")
    for x in stages["stages"]["prepare"]["full_query"]:
        console.print(f"* {x}")
    console.print()


###############################################################################
#
# Pipeline extensions
#
###############################################################################
def expected(result):
    """
    Returns the expected value from a turn. Used by mock models.
    """
    return get_turn(result)["expected"]


def passed_predicate(result, turn_index=None):
    """
    Predicate function to determine if the result is considered passing.
    This checks if the assessment stage's result is zero, indicating
    that the LLM response matches the expected answer.

    Used by the `format` and `summarize` sub-commands.
    """
    return get_stages(result, turn_index)["assess"]["cost"] == 0


###############################################################################
#
# Pipeline specification
#
###############################################################################
menu_pipeline_spec = PipelineSpec(
    # Pipeline name used in `gotag run <pipeline>.`
    name="menu",
    #
    # Pipeline description shown by `gotag pipelines.`
    description="A multi-turn menu ordering pipeline with Typescript menu pruning",
    # Defines default configuration values for the pipeline.
    configuration=configuration,
    # Defines the directed acyclic graph (DAG) of stage functions.
    create_dag=stages,
    # Required function to extract the expected answer from the test case.
    expected=expected,
    # Optional FormatterSpec used by the `format` commend to display a rich
    # transcript of the case.
    formatter=FormatterSpec(
        format_turn=format_turn,
    ),
    # Optional predicate determines whether a case is considered passing.
    # Used by the `format` and `summarize` sub-commands.
    passed_predicate=passed_predicate,
    # Optional SummarizerSpec used by the `summarize` command to
    # summarize the results of the run.
    summarizer=SummarizerSpec(
        columns=[
            ColumnSpec(name="cost", contents=cost_cell),
            keywords_column,
            ColumnSpec(name="user", contents=user_cell),
        ]
    ),
)


def go():
    main([menu_pipeline_spec])


if __name__ == "__main__":
    go()
