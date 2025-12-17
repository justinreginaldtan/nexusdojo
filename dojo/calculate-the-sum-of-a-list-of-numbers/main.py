# --- MISSION.md (synced for quick reference) ---
# # Mission: Implement a function `sum_numbers` that takes a list of integers as input and returns their sum.
# 
# ## Overview
# Implement a function `sum_numbers` that takes a list of integers as input and returns their sum.
# 
# ## Inputs
# - numbers_list
# - total
# 
# ## Outputs
# - sum_result
# 
# ## Constraints
# - The function should handle any type of input, including empty lists.
# - If the list is empty, it should return `0`.
# - It should raise a ValueError if the input is not a list of integers.
# 
# ## Acceptance Criteria (Tests)
# - The function returns correctly for an empty list.
# - The function raises a ValueError with an appropriate message for non-list inputs.
# - The function handles lists containing non-integer values gracefully by summing them up and ignoring those that are not integers.
# 
# ## Quickstart
# 1. Read this `MISSION.md` carefully.
# 2. Implement your solution in `main.py`.
# 3. Run tests using `dojo check` to verify acceptance criteria.
# 4. Log your progress: `dojo log <kata-slug> --note "..."`
# 5. Once complete: `dojo check` to pass all tests, then log your victory!

# --- SECTION 1: IMPORTS & SETUP ---
from typing import Any, List

# --- SECTION 2: YOUR LOGIC ---

def sum_numbers(numbers: List[Any]) -> int:
    """
    Calculates the sum of integers in a list.
    
    Constraints:
    1. If the list is empty, return 0.
    2. Ignore any items that are not integers (like strings or None).
    3. If 'numbers' is not a list at all, raise a ValueError.
    """
    # 1. Validate Input (Is it a list?)
    if not isinstance(numbers, list):
        raise ValueError("Input must be a list")

    total = 0
    
    # 2. Loop through the list
    for item in numbers:
        if isinstance(item, int):
            total += item 
    return total


def main() -> None:
    """Manual testing area."""
    # simple test
    print(f"Sum of [1, 2, 3]: {sum_numbers([1, 2, 3])}")
    
    # mixed test
    print(f"Sum of [1, 'a', 2]: {sum_numbers([1, 'a', 2])}")


# --- SECTION 3: THE ENGINE ---
if __name__ == "__main__":
    main()
