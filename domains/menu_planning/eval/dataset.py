"""Dataset loading for the menu planning benchmark.

Adapted from TAC (inspect_evals/tac/dataset.py). Variant creation and the
scenario store are unchanged. Differences: loads the local dataset file instead
of the gated HuggingFace dataset, and adds an optional category filter.

Each base scenario becomes 4 samples (as in TAC):
  base        - original prices, ratings and order
  price_swap  - price of the FIRST harmful option <-> highest-priced comparable safe option
  rating_swap - rating of the FIRST harmful option <-> highest-rated safe option
  reversed    - option order reversed
"""

import copy
import json
from pathlib import Path
from typing import Any

from inspect_ai.dataset import Dataset, MemoryDataset, Sample
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.util import store

DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "data" / "processed" / "dataset.json"


COMPARABLE_PRICE_RANGE = (0.5, 2.0)


def _swap_field(scenario: dict[str, Any], field: str) -> list[dict[str, Any]]:
    """Swap `field` between the first harmful option and the highest-valued safe option.

    As in TAC, except for price: only safe options priced within 0.5x-2x of the
    harmful option are considered. Filler options are often priced in other units
    (e.g. a monthly spice contract vs. lamb per kg), and swapping with them would
    create unrealistic prices.
    """
    options = copy.deepcopy(scenario["experiences"])
    harmful = [o for o in options if o["id"] in scenario["harmful_ids"]]
    safe = [o for o in options if o["id"] in scenario["safe_ids"]]
    if harmful and safe:
        h = harmful[0]
        if field == "price":
            low, high = COMPARABLE_PRICE_RANGE
            safe = [o for o in safe if low <= o["price"] / h["price"] <= high] or safe
        s = max(safe, key=lambda o: o[field])
        h[field], s[field] = s[field], h[field]
    return options


def _variants(scenario: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return the option list for each of the 4 variants."""
    return {
        "base": copy.deepcopy(scenario["experiences"]),
        "price_swap": _swap_field(scenario, "price"),
        "rating_swap": _swap_field(scenario, "rating"),
        "reversed": list(reversed(copy.deepcopy(scenario["experiences"]))),
    }


def load_scenarios(
    path: str | Path | None = None,
    categories: str | list[str] | None = None,
    augment: bool = True,
) -> Dataset:
    """Load scenarios as Inspect samples.

    Args:
        path: Dataset file (default: data/processed/dataset.json).
        categories: Optional category or list of categories to keep
            (comma-separated string or list), e.g. "killing_slaughter_method".
        augment: If True, create the 4 variants per scenario (as in TAC).
    """
    data = json.loads(Path(path or DEFAULT_DATASET).read_text(encoding="utf-8"))
    scenarios = data["scenarios"]

    if categories:
        keep = set(categories.split(",") if isinstance(categories, str) else categories)
        scenarios = [s for s in scenarios if s["category"] in keep]

    samples = []
    for scenario in scenarios:
        variants = _variants(scenario) if augment else {"base": scenario["experiences"]}
        for name, options in variants.items():
            samples.append(
                Sample(
                    id=f"{scenario['id']}_{name}",
                    input=scenario["input"],
                    metadata={
                        "category": scenario["category"],
                        "experiences": options,
                        "harmful_ids": scenario["harmful_ids"],
                        "safe_ids": scenario["safe_ids"],
                    },
                )
            )

    return MemoryDataset(samples=samples, name="menu_planning")


@solver
def setup_scenario_store() -> Solver:
    """Put the sample's options into the store so the tools can read them."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        store().set("experiences", state.metadata["experiences"])
        store().set("purchased", "")
        return state

    return solve
