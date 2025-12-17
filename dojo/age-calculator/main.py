# --- MISSION.md (synced for quick reference) ---
# # Mission: The Age Calculator
# 
# ## Overview
# Create a function `calculate_age(birth_year, current_year)` that returns an integer age.
# If `birth_year` is greater than `current_year`, raise `ValueError`.
# 
# ## Inputs
# - `birth_year` (int)
# - `current_year` (int)
# 
# ## Output
# - An integer age in years.
# 
# ## Rules
# - `age = current_year - birth_year`
# - Future birth years are invalid.
# 
# ## Acceptance Criteria (Tests)
# - `calculate_age(2000, 2025)` returns `25`
# - `calculate_age(2025, 2025)` returns `0`
# - `calculate_age(2030, 2025)` raises `ValueError`
# 
# ## Quickstart
# 1. Read this `MISSION.md`.
# 2. Edit `main.py`.
# 3. Run `dojo watch`.

from __future__ import annotations


def calculate_age(birth_year: int, current_year: int) -> int:
    """Return age in years given birth year and current year."""
    # TODO: Implement the mission rules.
    if birth_year > current_year:
        raise ValueError
    return current_year - birth_year


def main() -> None:
    print(calculate_age(2000, 2025))


if __name__ == "__main__":
    main()
