# --- SECTION 1: IMPORTS & SETUP ---
# Keep everything in this file so you can see how the pieces connect.
# If you need more standard libraries later (argparse, json, pathlib, etc.), import them here.


# --- SECTION 2: YOUR LOGIC (Write Code Here) ---
def main() -> None:
    """Entry point for your script; replace the print with your own logic."""
    message = "Hello from {{IDEA}}"  # Example output to prove the script runs.
    print(message)  # Print is fine for simple scripts; swap with real work as needed.


# --- SECTION 3: THE ENGINE (Don't Touch Yet) ---
if __name__ == "__main__":
    # This guard ensures main() runs only when executing `python main.py`
    # (and not when importing this file in tests).
    main()
