"""
This module demonstrates the implementation of a simple, linear pipeline
for a restaurant ordering bot.

The pipeline has the following stages:
    - prepare: prepares the system, agent, and user messages for the
               for the model. Uses a jinga2 template to format the system
               message.
    - infer: invokes the model to generate a response.
    - extract: extracts a JSON shopping cart from the model response.
    - assess: compares the model response to the expected answer.

The pipeline also provides implementations the following sub-commnads,
which can be invoked from the command line:
    - summarize: prints a summary of the results.
    - format: pretty prints the each case
    - compare: compares two pipeline runs.
"""

from glom import glom
import json
import os
from rich.console import Console
from rich.table import Table
from rich.text import Text
import sys
import tiktoken

# Add the parent directory to the sys.path so that we can import from the
# gotaglio package, as if it had been installed.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from gotaglio.exceptions import ExceptionContext
from gotaglio.helpers import IdShortener
from gotaglio.main import main
from gotaglio.models import Model
from gotaglio.pipeline import Internal, Pipeline, Prompt
from gotaglio.repair import Repair
from gotaglio.shared import build_template

from ts_type_filter import (
    collect_string_literals,
    build_type_index,
    build_filtered_types,
    parse
)

# from menu import type_defs


class MenuPipeline(Pipeline):
    # The Pipeline abstract base class requires _name and _description.
    # These are used by the Registry to list and instantiate pipelines.
    # The `pipelines` subcommand will print a list of available pipelines,
    # with their names and descriptions.
    _name = "menu"
    _description = "An example pipeline for an LLM-based food ordering bot."

    def __init__(self, registry, replacement_config, flat_config_patch):
        """
        Initializes the pipeline with the given Registry and configuration.

        Args:
          - registry: an instance of class Registry. Provides access to models.
          - replacement_config: a configuration that should be used instead of the
              default configuration provided by the pipeline. The replacement_config
              is used when rerunning a case from a log file.
          - flat_config_patch: a dictionary of glom-style key-value pairs that that
              override individual configuration values. These key-value pairs come from
              the command line and allow one to adjust model parameters or rerun a case
              with, say, a different model.
        """

        # Default configuration values for each pipeline stage.
        # The structure and interpretation of each configuration dict is
        # dictated by the needs of corresponding pipeline stage.
        #
        # An instance of Prompt indicates that the value must be provided on
        # the command line. In this case, the user would need to provide values
        # for the following keys on the command line:
        #   - prepare.template
        #   - infer.model.name
        #
        # An instance of Internal indicates that the value is provided by the
        # pipeline runtime. Using a value of Internal will prevent the
        # corresponding key from being displayed in help messages.
        #
        # There is no requirement to define a configuration dict for each stage.
        # It is the implementation of the pipeline that determines which stages
        # require configuration dicts.
        default_config = {
            "prepare": {
                "compress": False,
                "menu": "data/menu.ts",
                "prune": True,
                "template": "data/template.txt",
                "template_text": Internal(),
            },
            "infer": {
                "model": {
                    "name": "gpt4o",
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
        super().__init__(default_config, replacement_config, flat_config_patch)

        # Load type system in constructor, rather than stages(), so that
        # it is available for format().
        # Read the contents of menu.ts into a string.
        # Use utf8 because of terms like "jalapeño".
        filename = glom(self.config(), "prepare.menu")
        with open(filename, "r", encoding="utf-8") as file:
            menu_text = file.read()

        # Parse the TypeScript type definitions
        self.type_defs = parse(menu_text)


        # Save registry here for later use in the stages() method.
        self._registry = registry

        # Construct and register some model mocks, specific to this pipeline.
        Flakey(registry, {})
        Perfect(registry, {})

    # The structure of the pipeline is defined by the stages() method.
    # This example demonstrates a simple, linear pipeline with four stages.
    def stages(self):
        #
        # Perform some setup here so that any initialization errors encountered
        # are caught before running the cases.
        #

        # Compile the jinja2 template used in the `prepare` stage.
        template = build_template(
            self.config(),
            "prepare.template",
            "prepare.template_text",
        )

        symbols, indexer = build_type_index(self.type_defs)

        # Instantiate the model for the `infer` stage.
        model = self._registry.model(glom(self.config(), "infer.model.name"))

        #
        # Define the pipeline stage functions
        #
        """
        Define the pipeline stage functions. Each stage function is a coroutine
        that takes a context dictionary as an argument.

        context["case"] has the `case` data for the current case. Typically
        this comes from the cases JSON file specified as a parameter to the
        `run` sub-command.

        context["stages"][name] has the return value for stage `name`. Note
        that context["stages"][name] will only be defined if after the stage
        has to conclusion without raising an exception.

        Note that a stage function will only be invoked if the previous stage
        has completed with a return value. 
        """

        # Create the system and user messages
        async def prepare(context):
            # Prune the menu based on terms in the query and the cart
            user_query = context["case"]["query"]
            cart = context["case"]["cart"]
            cart_literals = collect_string_literals(cart)
            full_query = [user_query] + cart_literals
            reachable = build_filtered_types(self.type_defs, symbols, indexer, full_query)
            compress = (
                str(glom(self.config(), "prepare.compress", default=False)) == "True"
            )
            pruned = (
                format_menu(reachable, compress)
                if str(self.config()["prepare"]["prune"]) == "True"
                else format_menu(self.type_defs, compress)
            )

            messages = [
                {"role": "system", "content": await template({"menu": pruned})},
                {"role": "assistant", "content": json.dumps(cart, indent=2)},
            ]
            # case = context["case"]
            # for c in case["turns"][:-1]:
            #     messages.append({"role": "user", "content": c["query"]})
            #     messages.append(
            #         {
            #             "role": "assistant",
            #             "content": json.dumps(c["expected"], indent=2),
            #         }
            #     )
            messages.append({"role": "user", "content": context["case"]["query"]})

            return {
                "messages": messages,
                "full_query": full_query,
            }

        # Invoke the model to generate a response
        async def infer(context):
            return await model.infer(context["stages"]["prepare"]["messages"], context)

        # Attempt to extract a JSON shopping cart from the model response.
        # Note that this method will raise an exception if the response is not
        # a number.
        async def extract(context):
            with ExceptionContext(f"Extracting JSON from LLM response."):
                text = context["stages"]["infer"]

                # Strip off fenced code block markers, if present.
                marker = "```json\n"
                if text.startswith(marker):
                    text = text[len(marker) :]
                text = text.strip("```")
                return json.loads(text)

        # Compare the model response to the expected shopping cart.
        async def assess(context):
            repair = Repair("id", "options", [], ["name"], "name")
            repair.resetIds()
            observed = repair.addIds(context["stages"]["extract"]["items"])
            expected = repair.addIds(context["case"]["expected"]["items"])
            return repair.diff(observed, expected)

        # The pipeline stages will be executed in the order specified in the
        # dictionary returned by the stages() method. The keys of the
        # dictionary are the names of the stages.
        return {
            "prepare": prepare,
            "infer": infer,
            "extract": extract,
            "assess": assess,
        }

    # This method is used to summarize the results of each a pipeline run.
    # It is invoked by the `run`, `rerun`, and `summarize` sub-commands.
    def summarize(self, make_console, runlog):
        console = make_console("text/plain")
        results = runlog["results"]
        if len(results) == 0:
            console.print("No results.")
        else:
            # To make the summary more readable, create a short, unique prefix
            # for each case id.
            short_id = IdShortener([result["case"]["uuid"] for result in results])

            # Using Table from the rich text library.
            # https://rich.readthedocs.io/en/stable/introduction.html
            table = Table(title=f"Summary for {runlog['uuid']}")
            table.add_column("id", justify="right", style="cyan", no_wrap=True)
            table.add_column("run", style="magenta")
            table.add_column("score", justify="right", style="green")
            table.add_column("keywords", justify="left", style="green")

            # Set up some counters for totals to be presented after the table.
            total_count = len(results)
            complete_count = 0
            passed_count = 0
            failed_count = 0
            error_count = 0

            # Add one row for each case.
            for result in results:
                succeeded = result["succeeded"]
                cost = result["stages"]["assess"]["cost"] if succeeded else None

                if succeeded:
                    complete_count += 1
                    if cost == 0:
                        passed_count += 1
                    else:
                        failed_count += 1
                else:
                    error_count += 1

                complete = (
                    Text("COMPLETE", style="bold green")
                    if succeeded
                    else Text("ERROR", style="bold red")
                )
                cost_text = "" if cost == None else f"{cost:.2f}"
                score = (
                    Text(cost_text, style="bold green")
                    if cost == 0
                    else Text(cost_text, style="bold red")
                )
                keywords = (
                    ", ".join(sorted(result["case"]["keywords"]))
                    if "keywords" in result["case"]
                    else ""
                )
                table.add_row(
                    short_id(result["case"]["uuid"]), complete, score, keywords
                )

            # Display the table and the totals.
            console.print(table)
            console.print()
            console.print(f"Total: {total_count}")
            console.print(
                f"Complete: {complete_count}/{total_count} ({(complete_count/total_count)*100:.2f}%)"
            )
            console.print(
                f"Error: {error_count}/{total_count} ({(error_count/total_count)*100:.2f}%)"
            )
            console.print(
                f"Passed: {passed_count}/{total_count} ({(passed_count/total_count)*100:.2f}%)"
            )
            console.print(
                f"Failed: {failed_count}/{total_count} ({(failed_count/total_count)*100:.2f}%)"
            )
            console.print()

    # If uuid_prefix is specified, format those cases whose uuids start with
    # uuid_prefix. Otherwise, format all cases.
    def format(self, make_console, runlog, uuid_prefix):
        console = make_console("text/markdown")
        # Lazily load the GPT-4o tokenizer here so that we don't slow down
        # other scenarios that don't need it.
        if not hasattr(self, "_tokenizer"):
            self._tokenizer = tiktoken.get_encoding("cl100k_base")

        compress = (
            str(glom(runlog, "metadata.pipeline.prepare.compress", default="False"))
            == "True"
        )

        complete = format_menu(self.type_defs, compress)
        complete_tokens = len(self._tokenizer.encode(complete))

        console.print(f"## Run: {runlog['uuid']}")

        results = runlog["results"]
        if len(results) == 0:
            console.print("No results.")
        else:
            # To make the summary more readable, create a short, unique prefix
            # for each case id.
            short_id = IdShortener([result["case"]["uuid"] for result in results])

            for result in results:
                if uuid_prefix and not result["case"]["uuid"].startswith(uuid_prefix):
                    continue
                console.print(f"## Case: {short_id(result['case']['uuid'])}")
                if result["succeeded"]:
                    cost = result["stages"]["assess"]["cost"]
                    if cost == 0:
                        console.print("**PASSED**  ")
                    else:
                        console.print(f"**FAILED:** cost={cost}  ")
                        # print(
                        #     f"**FAILED**: expected\n~~~json\n{json.dumps(result['case']["turns"][-1]['expected'], indent=2)}\n~~~\n\n"
                        # )
                    # print(result["case"]["comment"])
                    console.print()

                    console.print(
                        f"Keywords: {', '.join(result['case'].get('keywords', []))}  "
                    )

                    input_tokens = sum(
                        len(self._tokenizer.encode(message["content"]))
                        for message in result["stages"]["prepare"]["messages"]
                    )
                    console.print(f"Complete menu tokens: {complete_tokens}  ")
                    console.print(
                        f"Input tokens: {input_tokens}, output tokens: {len(self._tokenizer.encode(result['stages']['infer']))}"
                    )
                    console.print()

                    for x in result["stages"]["prepare"]["messages"]:
                        if x["role"] == "assistant" or x["role"] == "system":
                            console.print(f"**{x['role']}:**")
                            console.print("```json")
                            console.print(x["content"])
                            console.print("```")
                        elif x["role"] == "user":
                            console.print(f"**{x['role']}:** _{x['content']}_")
                        console.print()
                    console.print(f"**assistant:**")
                    console.print("```json")
                    console.print(json.dumps(result["stages"]["extract"], indent=2))
                    console.print("```")
                    console.print()

                    if cost > 0:
                        console.print("**Repairs:**")
                        for step in result["stages"]["assess"]["steps"]:
                            console.print(f"* {step}")
                    else:
                        console.print("**No repairs**")

                    console.print()
                    console.print("**Full query**:")
                    for x in result["stages"]["prepare"]["full_query"]:
                        console.print(f"* {x}")
                    console.print()

                else:
                    console.print("**ERROR**  ")
                    console.print(f"Error: {result['exception']['message']}")
                    console.print("~~~")
                    console.print(f"Traceback: {result['exception']['traceback']}")
                    console.print(f"Time: {result['exception']['time']}")
                    console.print("~~~")

    def compare(self, make_console, a, b):
        console = make_console("text/plain")
        console.print("TODO: compare()")

        if a["uuid"] == b["uuid"]:
            console.print(f"Run ids are the same.\n")
            self.summarize(a)
            return

        if a["metadata"]["pipeline"]["name"] != b["metadata"]["pipeline"]["name"]:
            console.print(
                f"Cannot perform comparison because pipeline names are different: A is '{
                    a['metadata']['pipeline']['name']
                }', B is '{
                    b['metadata']['pipeline']['name']
                }'"
            )
            return

        a_cases = {result["case"]["uuid"]: result for result in a["results"]}
        b_cases = {result["case"]["uuid"]: result for result in b["results"]}
        a_uuids = set(a_cases.keys())
        b_uuids = set(b_cases.keys())
        both = a_uuids.intersection(b_uuids)
        just_a = a_uuids - b_uuids
        just_b = b_uuids - a_uuids

        console.print(f"A: {a["uuid"]}")
        console.print(f"B: {b["uuid"]}")
        console.print("")
        console.print(f"{len(just_a)} case{'s' if len(just_a) != 1 else ''} only in A")
        console.print(f"{len(just_b)} case{'s' if len(just_b) != 1 else ''} only in B")
        console.print(f"{len(both)} cases in both A and B")
        console.print("")

        # TODO: handle no results case
        if len(both) == 0:
            console.print("There are no cases to compare.")
            console.print()
            # Fall through to print empty table

        # To make the summary more readable, create a short, unique prefix
        # for each case id.
        short_id = IdShortener(both)

        table = Table(title=f"Comparison of {"A, B"}", show_footer=True)
        table.add_column("id", justify="right", style="cyan", no_wrap=True)
        table.add_column("A", justify="right", style="magenta")
        table.add_column("B", justify="right", style="green")
        table.add_column("keywords", justify="left", style="green")

        rows = []
        pass_count_a = 0
        pass_count_b = 0
        for uuid in both:
            (text_a, order_a) = format_case(a_cases[uuid])
            (text_b, order_b) = format_case(b_cases[uuid])
            keywords = ", ".join(sorted(a_cases[uuid]["case"].get("keywords", [])))
            if order_a == 0:
                pass_count_a += 1
            if order_b == 0:
                pass_count_b += 1
            rows.append(
                (
                    (Text(short_id(uuid)), text_a, text_b, keywords),
                    order_b * 4 + order_a,
                )
            )
        rows.sort(key=lambda x: x[1])
        for row in rows:
            table.add_row(*row[0])

        table.columns[0].footer = "Total"
        table.columns[1].footer = Text(
            f"{pass_count_a}/{len(both)} ({(pass_count_a/len(both))*100:.0f}%)"
        )
        table.columns[2].footer = Text(
            f"{pass_count_b}/{len(both)} ({(pass_count_b/len(both))*100:.0f}%)"
        )

        console.print(table)
        console.print()


def format_case(result):
    if result["succeeded"]:
        if result["stages"]["assess"] == 0:
            return (Text("passed", style="bold green"), 0)
        else:
            return (Text("failed", style="bold red"), 1)
    else:
        return (Text("error", style="bold red"), 2)


class Flakey(Model):
    """
    A mock model class that cycles through
      1. returning the expected answer
      2. returning "hello world"
      3. raising an exception
    """

    def __init__(self, registry, configuration):
        self._counter = -1
        registry.register_model("flakey", self)

    async def infer(self, messages, result=None):
        self._counter += 1
        if self._counter % 3 == 0:
            return json.dumps(result["case"]["turns"][-1]["expected"])
        elif self._counter % 3 == 1:
            return "hello world"
        else:
            raise Exception("Flakey model failed")

    def metadata(self):
        return {}


class Perfect(Model):
    """
    A mock model class that always returns the expected answer
    from result["case"]["answer"]
    """

    def __init__(self, registry, configuration):
        registry.register_model("perfect", self)

    async def infer(self, messages, result=None):
        return json.dumps(result["case"]["expected"])

    def metadata(self):
        return {}


def format_menu(type_defs, compress=False):
    separator = "" if compress else "\n"
    return separator.join([x.format() for x in type_defs])


def go():
    main([MenuPipeline])


if __name__ == "__main__":
    go()
