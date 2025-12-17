# --- MISSION.md (synced for quick reference) ---
# # Mission: Hello Personalized World
# 
# ## Overview
# Create a function `greet(name)` that returns `Hello, {name}!`. If name is empty or None, return `Hello, World!`.
# 
# ## Inputs
# - `name` (string or None)
# 
# ## Outputs
# - A greeting string.
# 
# ## Constraints
# - Use f-strings.
# - Handle `None` and empty strings explicitly.
# 
# ## Acceptance Criteria (Tests)
# - `greet("Justin")` returns `"Hello, Justin!"`
# - `greet("")` returns `"Hello, World!"`
# - `greet(None)` returns `"Hello, World!"`
# 
# ## Quickstart
# 1. Read this `MISSION.md`.
# 2. Edit `main.py`.
# 3. Run `dojo watch`.

def greet(name: str | None) -> str:
    """
    Return a personalized greeting.
    """
    # TODO: Implement logic here
    if name == "" or name == None:
        return "Hello, World!"
    return f"Hello, {name}!"

def main():
    print(greet("Justin"))

if __name__ == "__main__":
    main()
