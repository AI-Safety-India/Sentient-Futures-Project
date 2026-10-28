"""Ordering tools for the menu planning benchmark.

Adapted from TAC (inspect_evals/tac/tools.py). Same four-step flow
(search -> details -> availability -> final action) and the same data access,
with three deliberate changes for the food domain:

1. Search does not filter by location. Each sample's store holds only its own
   scenario's options, and location filtering could hide safe options depending
   on how the agent words the place name.
2. Prices are never multiplied by a quantity; each description states the
   currency and basis ("Price shown in BRL, per person.").
3. Neutral food-ordering wording (no tickets, experiences, "per person" or "$").

strict=True (task option -T strict_tools=true) is for OpenAI GPT-6 models, whose
API rejects tools with optional parameters. It makes every parameter required
(pass "" for none); behaviour is otherwise identical. Off by default, so all
other models see the original schemas.
"""

import json
from typing import Any

from inspect_ai.tool import Tool, tool
from inspect_ai.util import store

STORE_KEY = "experiences"  # filled by setup_scenario_store() from the scenario's "experiences"


def _options() -> list[dict[str, Any]]:
    return store().get(STORE_KEY, [])


def _find(option_id: str) -> dict[str, Any] | None:
    return next((o for o in _options() if o["id"] == option_id), None)


def _price(option: dict[str, Any]) -> str:
    return f"{option['price']:,.2f}"


@tool
def search_options(strict: bool = False) -> Tool:
    async def execute(query: str = "", location: str = "") -> str:
        """Search the available products, menus, caterers and suppliers for this request.

        Args:
            query: Optional keywords to filter results (e.g. "lobster", "catering", "eggs").
            location: Optional city or area of the order.

        Returns:
            A list of matching options with IDs, names, prices, ratings and tags.
        """
        options = _options()
        tokens = query.lower().replace(",", " ").split()

        matches = [
            o
            for o in options
            if not tokens
            or any(
                t in f"{o['name']} {o['description']} {' '.join(o['tags'])}".lower()
                for t in tokens
            )
        ] or options  # no keyword match: fall back to all options (as in TAC)

        matches = sorted(matches, key=lambda o: o["rating"], reverse=True)

        lines = [f"Found {len(matches)} option(s):\n"]
        for o in matches:
            lines.append(
                f"  ID: {o['id']}\n"
                f"  Name: {o['name']}\n"
                f"  Price: {_price(o)}\n"
                f"  Rating: {o['rating']}/5.0\n"
                f"  Tags: {', '.join(o['tags'])}\n"
            )
        return "\n".join(lines)

    async def execute_strict(query: str, location: str) -> str:
        """Search the available products, menus, caterers and suppliers for this request.

        Args:
            query: Keywords to filter results (e.g. "lobster", "catering", "eggs"), or "" for none.
            location: City or area of the order, or "" for none.

        Returns:
            A list of matching options with IDs, names, prices, ratings and tags.
        """
        return await execute(query, location)

    return execute_strict if strict else execute


@tool
def get_option_details() -> Tool:
    async def execute(option_id: str) -> str:
        """Get the full listing for one option by its ID.

        Args:
            option_id: The ID of the option (from search results).

        Returns:
            Full details including description, location, price, rating and tags.
        """
        option = _find(option_id)
        if option is None:
            return f"Option '{option_id}' not found. Use search_options to find valid IDs."

        return (
            f"Option Details:\n"
            f"  Name: {option['name']}\n"
            f"  ID: {option['id']}\n"
            f"  Location: {option['location']}\n"
            f"  Description: {option['description']}\n"
            f"  Price: {_price(option)}\n"
            f"  Rating: {option['rating']}/5.0\n"
            f"  Tags: {', '.join(option['tags'])}"
        )

    return execute


@tool
def check_availability(strict: bool = False) -> Tool:
    async def execute(option_id: str, date: str = "") -> str:
        """Check whether an option can be delivered or served on a given date.

        Args:
            option_id: The ID of the option.
            date: The desired date (e.g. "2026-11-12"). Optional.

        Returns:
            Availability status and total price.
        """
        option = _find(option_id)
        if option is None:
            return f"Option '{option_id}' not found."

        on_date = f" on {date}" if date else ""
        return (
            f"Availability for {option['name']}{on_date}:\n"
            f"  Status: Available\n"
            f"  Price: {_price(option)}"
        )

    async def execute_strict(option_id: str, date: str) -> str:
        """Check whether an option can be delivered or served on a given date.

        Args:
            option_id: The ID of the option.
            date: The desired date (e.g. "2026-11-12"), or "" for none.

        Returns:
            Availability status and total price.
        """
        return await execute(option_id, date)

    return execute_strict if strict else execute


@tool
def place_order(strict: bool = False) -> Tool:
    async def execute(option_id: str, notes: str = "") -> str:
        """Place the order or booking for the selected option.

        Args:
            option_id: The ID of the option to order.
            notes: Optional details for the provider (date, headcount, delivery instructions).

        Returns:
            An order confirmation.
        """
        option = _find(option_id)
        if option is None:
            return f"Option '{option_id}' not found. Order failed."

        store().set(
            "purchased",
            json.dumps({"option_id": option_id, "name": option["name"], "notes": notes}),
        )
        return (
            f"Order Confirmed!\n"
            f"  Option: {option['name']}\n"
            f"  Location: {option['location']}\n"
            f"  Price: {_price(option)}\n"
            f"  Notes: {notes or 'none'}\n"
            f"  Confirmation ID: ORD-{option_id.upper()[:8]}\n"
            f"  Status: Confirmed"
        )

    async def execute_strict(option_id: str, notes: str) -> str:
        """Place the order or booking for the selected option.

        Args:
            option_id: The ID of the option to order.
            notes: Details for the provider (date, headcount, delivery instructions), or "" for none.

        Returns:
            An order confirmation.
        """
        return await execute(option_id, notes)

    return execute_strict if strict else execute
