# --- MISSION.md (synced for quick reference) ---
# # Mission: Develop a simple command-line calculator in Python that performs addition, subtraction, multiplication, and division on two integers.
# 
# ## Overview
# Develop a simple command-line calculator in Python that performs addition, subtraction, multiplication, and division on two integers.
# 
# ## Inputs
# - A string representing the first integer
# - A string representing the second integer
# 
# ## Outputs
# - An integer representing the sum of the two integers
# - An integer representing the difference between the two integers
# - An integer representing the product of the two integers
# - An float representing the quotient of the two integers (if applicable)
# 
# ## Constraints
# - Error handling must be implemented to gracefully handle exceptions, such as type errors or division by zero.
# - Type hints should be used to ensure that the inputs are correctly interpreted.
# - The function should be optimized for performance with large input sizes.
# 
# ## Acceptance Criteria (Tests)
# - The function should return the correct result for valid inputs.
# - The function should raise a ValueError for invalid inputs (e.g., non-integer strings or division by zero).
# 
# ## Quickstart
# 1. Read this `MISSION.md` carefully.
# 2. Implement your solution in `main.py`.
# 3. Run tests using `dojo check` to verify acceptance criteria.
# 4. Log your progress: `dojo log <kata-slug> --note "..."`
# 5. Once complete: `dojo check` to pass all tests, then log your victory!

"""Basic calculator -- Build add/subtract/multiply/divide CLI with input validation.

MISSION SPECS:

## Overview
Develop a simple command-line calculator in Python that performs addition, subtraction, multiplication, and division on two integers.

## Inputs
- A string representing the first integer
- A string representing the second integer

## Outputs
- An integer representing the sum of the two integers
- An integer representing the difference between the two integers
- An integer representing the product of the two integers
- An float representing the quotient of the two integers (if applicable)

## Constraints
- Error handling must be implemented to gracefully handle exceptions, such as type errors or division by zero.
- Type hints should be used to ensure that the inputs are correctly interpreted.
- The function should be optimized for performance with large input sizes.

## Acceptance Criteria (Tests)
- The function should return the correct result for valid inputs.
- The function should raise a ValueError for invalid inputs (e.g., non-integer strings or division by zero).

## Quickstart
1. Read this `MISSION.md` carefully.
2. Implement your solution in `main.py`.
3. Run tests using `dojo check` to verify acceptance criteria.
4. Log your progress: `dojo log <kata-slug> --note "..."`
5. Once complete: `dojo check` to pass all tests, then log your victory!
"""
from typing import Tuple


def parse_input(raw: str) -> Tuple[str, float, float]:
    """
    Parse input of the form "<op> <num1> <num2>" and return components.
    Supported ops: add, sub, mul, div, +, -, *, /
    """
    parts = raw.strip().split()
    if len(parts) != 3:
        raise ValueError("Input must be '<op> <num1> <num2>'")
    op, a_str, b_str = parts
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError as exc:
        raise ValueError("Inputs must be numeric") from exc
    return op, a, b


def calculate(operation: str, num1: float, num2: float) -> float:
    """Perform arithmetic based on the operation token."""
    if operation in {"add", "+"}:
        return num1 + num2
    if operation in {"sub", "-"}:
        return num1 - num2
    if operation in {"mul", "*"}:
        return num1 * num2
    if operation in {"div", "/"}:
        if num2 == 0:
            raise ValueError("Division by zero")
        return num1 / num2
    raise ValueError(f"Unsupported operation: {operation}")


def main() -> None:
    print("Basic Calculator ready. Example: 'add 2 3'")


if __name__ == "__main__":
    main()
