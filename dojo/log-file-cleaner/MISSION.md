# Mission: The Log File Cleaner

## Overview
You are given a list of messy log lines (strings). Return a **clean** list containing **only** the lines that include `"ERROR"`.

## Inputs
- `lines` (list[str]): e.g. `[" ERROR: fail ", "INFO: ok"]`

## Output
- A list of cleaned strings:
  - Keep only lines containing `"ERROR"`
  - Strip leading/trailing whitespace from the kept lines

## Rules
- Preserve the original text (besides trimming whitespace).
- If there are no error lines, return an empty list.

## Acceptance Criteria (Tests)
- Filters to only `"ERROR"` lines
- Strips whitespace

## Quickstart
1. Read this `MISSION.md`.
2. Edit `main.py`.
3. Run `dojo watch`.
