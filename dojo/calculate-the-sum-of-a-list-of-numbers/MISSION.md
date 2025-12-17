# Mission: Implement a function `sum_numbers` that takes a list of integers as input and returns their sum.

## Overview
Implement a function `sum_numbers` that takes a list of integers as input and returns their sum.

## Inputs
- numbers_list
- total

## Outputs
- sum_result

## Constraints
- The function should handle any type of input, including empty lists.
- If the list is empty, it should return `0`.
- It should raise a ValueError if the input is not a list of integers.

## Acceptance Criteria (Tests)
- The function returns correctly for an empty list.
- The function raises a ValueError with an appropriate message for non-list inputs.
- The function handles lists containing non-integer values gracefully by summing them up and ignoring those that are not integers.

## Quickstart
1. Read this `MISSION.md` carefully.
2. Implement your solution in `main.py`.
3. Run tests using `dojo check` to verify acceptance criteria.
4. Log your progress: `dojo log <kata-slug> --note "..."`
5. Once complete: `dojo check` to pass all tests, then log your victory!