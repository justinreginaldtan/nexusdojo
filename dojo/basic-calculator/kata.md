# Basic Calculator

A simple CLI calculator for addition, subtraction, multiplication, and division.

## Functions to implement
- calc_main: The main function that takes user input, parses it, and executes the appropriate calculation.
  - Example args: ['4 + 3'], kwargs: {}, output: 7
- calculate_operation: A function to perform the calculation based on the given operation.
  - Example args: ['+', 4.0, 3.0], kwargs: {}, output: 7.0
- validate_input: A function to validate the input string for arithmetic operations.
  - Example args: ['4 + 3'], kwargs: {}, output: True

## Quickstart
- Run tests: python -m unittest
- Run script: python main.py