"""Menu planning benchmark tasks (TAC extension).

Adapted from TAC (inspect_evals/tac/tac.py). Two tasks that differ ONLY in the
system prompt, with TAC's solver order and settings:
  menu_planning         - neutral prompt (OrderHub)
  menu_planning_welfare - ethical-brand prompt (Harvest Table)

Run:
  uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model <MODEL>
  uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model <MODEL>
Options (-T): dataset=<path>, categories=<category[,category]>,
  strict_tools=true (OpenAI GPT-6 only: their API rejects optional tool
  parameters, so all parameters become required with "" for none; see tools.py)
"""

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import system_message, use_tools

from dataset import load_scenarios, setup_scenario_store
from multiturn import confirm_to_complete
from prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_WELFARE
from scorer import menu_planning_scorer
from tools import check_availability, get_option_details, place_order, search_options

VERSION = "1.0"


def _build_task(
    system_prompt: str,
    condition: str,
    dataset: str | None,
    categories: str | None,
    strict_tools: bool,
) -> Task:
    tools = [
        search_options(strict=strict_tools),
        get_option_details(),
        check_availability(strict=strict_tools),
        place_order(strict=strict_tools),
    ]
    return Task(
        dataset=load_scenarios(path=dataset, categories=categories),
        solver=[
            setup_scenario_store(),
            system_message(system_prompt),
            use_tools(tools),
            confirm_to_complete(),
        ],
        scorer=menu_planning_scorer(),
        epochs=3,
        max_messages=30,
        config=GenerateConfig(max_tokens=16384, reasoning_effort="medium"),
        version=VERSION,
        metadata={"benchmark_version": VERSION, "condition": condition, "strict_tools": strict_tools},
    )


@task
def menu_planning(
    dataset: str | None = None, categories: str | None = None, strict_tools: bool = False
) -> Task:
    """Neutral condition: OrderHub ordering runtime, no values language."""
    return _build_task(SYSTEM_PROMPT, "neutral", dataset, categories, strict_tools)


@task
def menu_planning_welfare(
    dataset: str | None = None, categories: str | None = None, strict_tools: bool = False
) -> Task:
    """Ethical condition: Harvest Table brand naming people, animals and places."""
    return _build_task(SYSTEM_PROMPT_WELFARE, "ethical", dataset, categories, strict_tools)
