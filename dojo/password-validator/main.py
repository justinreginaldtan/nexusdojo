# --- MISSION.md (synced for quick reference) ---
# # Mission: The Password Validator
# 
# ## Overview
# Create a function `is_valid_password(password)` that returns `True` only when:
# 1) The password length is **greater than 8** characters, and
# 2) The password contains **at least one digit**.
# 
# ## Inputs
# - `password` (str)
# 
# ## Output
# - `True` or `False`
# 
# ## Rules
# - Length must be **> 8** (e.g., 9+ characters).
# - Digit check can use `str.isdigit()`.
# 
# ## Acceptance Criteria (Tests)
# - Valid password returns `True`
# - Missing digit returns `False`
# - Too short returns `False`
# 
# ## Quickstart
# 1. Read this `MISSION.md`.
# 2. Edit `main.py`.
# 3. Run `dojo watch`.

from __future__ import annotations


def is_valid_password(password: str) -> bool:
    """Return True if the password meets the mission rules."""
    # TODO: Implement the mission rules.
    return False


def main() -> None:
    print(is_valid_password("abcd12345"))


if __name__ == "__main__":
    main()
