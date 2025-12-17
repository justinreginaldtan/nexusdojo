# --- MISSION.md (synced for quick reference) ---
# # Mission: The Inventory Aggregator
# 
# ## Overview
# Given a list of item names, return a dictionary mapping each item to its count.
# 
# ## Inputs
# - `items` (list[str]) e.g. `["apple", "apple", "banana"]`
# 
# ## Output
# - `dict[str, int]` e.g. `{"apple": 2, "banana": 1}`
# 
# ## Rules
# - Count every occurrence.
# - Use a dictionary (`dict`) to aggregate counts.
# 
# ## Acceptance Criteria (Tests)
# - Aggregates counts correctly
# - Returns an empty dict for an empty list
# 
# ## Quickstart
# 1. Read this `MISSION.md`.
# 2. Edit `main.py`.
# 3. Run `dojo watch`.

from __future__ import annotations


def aggregate_inventory(items: list[str]) -> dict[str, int]:
    """Return a count map for the given items."""
    # TODO: Implement the mission rules.
    return {}


def main() -> None:
    print(aggregate_inventory(["apple", "apple", "banana"]))


if __name__ == "__main__":
    main()
