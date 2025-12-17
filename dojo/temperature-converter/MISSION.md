# Mission: The Temperature Converter

## Overview
Create a function `convert_temp(value, scale)` that converts a temperature between Celsius and Fahrenheit.

## Inputs
- `value` (float)
- `scale` (str): `"C"` or `"F"` indicating the *input* scale.
  - `"C"` means `value` is Celsius → return Fahrenheit
  - `"F"` means `value` is Fahrenheit → return Celsius

## Output
- The converted temperature as a float.

## Rules
- `F = C * 9/5 + 32`
- `C = (F - 32) * 5/9`
- If `scale` is not `"C"` or `"F"`, raise `ValueError`.

## Acceptance Criteria (Tests)
- `convert_temp(0, "C")` returns `32.0`
- `convert_temp(100, "C")` returns `212.0`
- `convert_temp(32, "F")` returns `0.0`
- Invalid `scale` raises `ValueError`

## Quickstart
1. Read this `MISSION.md`.
2. Edit `main.py`.
3. Run `dojo watch`.
