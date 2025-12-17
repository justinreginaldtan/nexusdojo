# --- MISSION.md (synced for quick reference) ---
# # Mission: The Log File Cleaner
# 
# ## Overview
# You are given a list of messy log lines (strings). Return a **clean** list containing **only** the lines that include `"ERROR"`.
# 
# ## Inputs
# - `lines` (list[str]): e.g. `[" ERROR: fail ", "INFO: ok"]`
# 
# ## Output
# - A list of cleaned strings:
#   - Keep only lines containing `"ERROR"`
#   - Strip leading/trailing whitespace from the kept lines
# 
# ## Rules
# - Preserve the original text (besides trimming whitespace).
# - If there are no error lines, return an empty list.
# 
# ## Acceptance Criteria (Tests)
# - Filters to only `"ERROR"` lines
# - Strips whitespace
# 
# ## Quickstart
# 1. Read this `MISSION.md`.
# 2. Edit `main.py`.
# 3. Run `dojo watch`.

from __future__ import annotations


def clean_errors(lines: list[str]) -> list[str]:
    """Return a cleaned list of only the log lines that contain 'ERROR'."""
    # TODO: Implement the mission rules.
    error_lines = []

    for log in lines:
        if "ERROR" in log:
            error_lines.append(log.strip())

    return error_lines


def main() -> None:
    sample = [" ERROR: fail ", "INFO: ok", "ERROR: disk full", " WARNING "]
    print(clean_errors(sample))


if __name__ == "__main__":
    main()
