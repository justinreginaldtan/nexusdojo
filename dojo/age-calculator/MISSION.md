# Mission: The Age Calculator

## Overview
Create a function `calculate_age(birth_year, current_year)` that returns an integer age.
If `birth_year` is greater than `current_year`, raise `ValueError`.

## Inputs
- `birth_year` (int)
- `current_year` (int)

## Output
- An integer age in years.

## Rules
- `age = current_year - birth_year`
- Future birth years are invalid.

## Acceptance Criteria (Tests)
- `calculate_age(2000, 2025)` returns `25`
- `calculate_age(2025, 2025)` returns `0`
- `calculate_age(2030, 2025)` raises `ValueError`

## Quickstart
1. Read this `MISSION.md`.
2. Edit `main.py`.
3. Run `dojo watch`.
