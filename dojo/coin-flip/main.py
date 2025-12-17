# --- MISSION.md (synced for quick reference) ---
# # Mission: Write a Python function `coin_flip()` that simulates flipping a coin and returns 'Heads' or 'Tails'. The function should handle all possible errors gracefully, such as invalid input types.
# 
# ## Overview
# Write a Python function `coin_flip()` that simulates flipping a coin and returns 'Heads' or 'Tails'. The function should handle all possible errors gracefully, such as invalid input types.
# 
# ## Inputs
# - None
# 
# ## Outputs
# - {'type': 'str', 'description': "The result of the coin flip ('Heads' or 'Tails')"}
# 
# ## Constraints
# - Input should be a valid string for coin toss
# - Function must raise ValueError if input is not a valid string
# - Function must handle file I/O errors gracefully
# 
# ## Acceptance Criteria (Tests)
# - Function should return correct value for 'Heads' and 'Tails'
# - Function should raise ValueError for invalid input
# - Function should handle file I/O errors gracefully without crashing the program
# 
# ## Quickstart
# 1. Read this `MISSION.md` carefully.
# 2. Implement your solution in `main.py`.
# 3. Run tests using `dojo check` to verify acceptance criteria.
# 4. Log your progress: `dojo log <kata-slug> --note "..."`
# 5. Once complete: `dojo check` to pass all tests, then log your victory!

"""Coin Flip -- crisp spec

MISSION SPECS:

## Overview
Write a Python function `coin_flip()` that simulates flipping a coin and returns 'Heads' or 'Tails'. The function should handle all possible errors gracefully, such as invalid input types.

## Inputs
- None

## Outputs
- {'type': 'str', 'description': "The result of the coin flip ('Heads' or 'Tails')"}

## Constraints
- Input should be a valid string for coin toss
- Function must raise ValueError if input is not a valid string
- Function must handle file I/O errors gracefully

## Acceptance Criteria (Tests)
- Function should return correct value for 'Heads' and 'Tails'
- Function should raise ValueError for invalid input
- Function should handle file I/O errors gracefully without crashing the program

## Quickstart
1. Read this `MISSION.md` carefully.
2. Implement your solution in `main.py`.
3. Run tests using `dojo check` to verify acceptance criteria.
4. Log your progress: `dojo log <kata-slug> --note "..."`
5. Once complete: `dojo check` to pass all tests, then log your victory!
"""
# --- SECTION 1: IMPORTS & SETUP ---
# Keep everything in this file so you can see how the pieces connect.
# If you need more standard libraries later (argparse, json, pathlib, etc.), import them here.


# --- SECTION 2: YOUR LOGIC (Write Code Here) ---
def main() -> None:
    """Entry point for your script; replace the print with your own logic."""
    message = "Hello from Coin Flip -- crisp spec"  # Example output to prove the script runs.
    print(message)  # Print is fine for simple scripts; swap with real work as needed.


# --- SECTION 3: THE ENGINE (Don't Touch Yet) ---
if __name__ == "__main__":
    # This guard ensures main() runs only when executing `python main.py`
    # (and not when importing this file in tests).
    main()
