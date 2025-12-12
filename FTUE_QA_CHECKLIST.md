# 🚀 NexusDojo: First-Time User Experience QA Checklist

**Goal:** Ensure the app guides a new user seamlessly from installation to completing their first drill, demonstrating all core features.

---

### **Phase 1: The Fresh Start**

1.  **Clean Workspace:**
    *   **Action:** In your terminal, navigate to the `nexusdojo` project root.
    *   **Command:** `rm -rf dojo notes`
    *   **Expected:** The `dojo/` and `notes/` folders are deleted. You are starting fresh.

2.  **Launch the Dojo:**
    *   **Action:** Make sure your virtual environment is activated.
    *   **Command:** `source .venv/bin/activate` (if not already active)
    *   **Command:** `dojo menu`
    *   **Expected:**
        *   The screen clears.
        *   You see the `👋 WELCOME` panel, stating "INITIALIZING SYSTEM..." and "Welcome to NEXUS DOJO."

---

### **Phase 2: Onboarding Wizard**

1.  **Profile Setup:**
    *   **Action:** The prompt "Ready to configure your profile? [y/n]:" appears.
    *   **Expected:**
        *   Type `y` and press Enter.
        *   The prompt "What should the system call you? [Engineer]:" appears.
        *   Type `Reginald` (or your preferred name) and press Enter.
        *   You see "[green]Identity confirmed: Reginald. Access granted.[/green]".
        *   The prompt "[bold cyan]Step 2: The Protocol[/bold cyan]" appears.

2.  **Workflow Introduction:**
    *   **Action:** Read the "Recommended Workflow" Markdown panel.
    *   **Command:** Press Enter when prompted "Press Enter to enter the Dojo".
    *   **Expected:**
        *   The screen clears.
        *   You are presented with the main `NEXUS DOJO` dashboard.
        *   The dashboard shows "Welcome back, Reginald."
        *   "Total XP: 0", "Completed Drills: 0".
        *   The menu options clearly show the "Lobby Menu" (7 options, e.g., "Quick Train", "Start New Session").

---

### **Phase 3: The First Drill (Python Warmup)**

1.  **Initiate Quick Train:**
    *   **Action:** Select option `1` (⚡ Quick Train (AI-Guided)) and press Enter.
    *   **Expected:**
        *   You see "[bold green]First time? Let's start with the basics.[/bold green]".
        *   A panel appears: "⚡ Quick Train: Python (tutorial)" with the idea "Python Warmup -- Create a script that prints a greeting and adds two numbers."
        *   The prompt "[dim]Launching in 3 seconds... (Ctrl+C to cancel)[/dim]" appears.

2.  **Launch Environment:**
    *   **Action:** If prompted "Start Pomodoro session? (25 min) [y/n]", type `n` and Enter. (To keep it simple for the first run).
    *   **Expected:**
        *   If `tmux` is running, your terminal splits:
            *   Left Pane: `nvim` opens with `main.py` and `MISSION.md` in buffers.
            *   Right Pane: `dojo watch` starts, showing "👀 SENSEI WATCH MODE" and `FOCUS TIMER: 00:00`.
        *   If `tmux` is NOT running, `nvim` opens, taking over your entire terminal. (You'll need to exit `nvim` later to get back to the prompt).

3.  **Mission Inspection (Inside Neovim):**
    *   **Action:** In Neovim, observe the contents of `main.py` (it should be the active buffer).
    *   **Expected:** The `main.py` file should contain:
        *   A docstring with the "Python Warmup" mission specs.
        *   Placeholder `main()` function.
        *   Basic imports relevant to the mission (e.g., `import os` might be there if mission text had "env").

4.  **Create Test File:**
    *   **Action:** Create a simple test file `tests/test_main.py` in the kata directory and add some basic tests for the `hello_world` and `add` functions. (The system doesn't auto-generate these for the Warmup yet, so you'll do it manually this first time to test the loop).

---

### **Phase 4: Coding & Feedback Loop**

1.  **Code the Solution:**
    *   **Action:** In `main.py`, add the required code.
    ```python
    def hello_world():
        return "Hello World"

    def add(a, b):
        return a + b

    def main():
        print(hello_world())
        print(f"Result of 5 + 3: {add(5, 3)}") # Example usage
    ```
    *   **Action:** Save `main.py` (`:w` in Neovim).
    *   **Expected (Watch Pane):**
        *   The `dojo watch` pane should detect the change and run tests.
        *   It should show `ALL TESTS PASSED` in a green panel.
        *   It prints `[dim]✔ Logged to history.[/dim]`.

2.  **Simulate Failure:**
    *   **Action:** Intentionally break `add` in `main.py` (e.g., `return a - b`). Save (`:w`).
    *   **Expected (Watch Pane):**
        *   The `dojo watch` pane detects the change.
        *   A `Panel` with a red border and `❌ TESTS FAILED` title appears.
        *   An "AI Diagnosis" panel provides a hint.

3.  **Fix and Pass:**
    *   **Action:** Fix `add` back to `return a + b`. Save (`:w`).
    *   **Expected (Watch Pane):**
        *   Tests pass again, green success message.

---

### **Phase 5: Post-Drill & Resume**

1.  **Exit Environment:**
    *   **Action:** Exit Neovim (`:q` in Neovim).
    *   **Expected:** You are returned to the `dojo menu` (Lobby Mode).

2.  **Verify Progression:**
    *   **Action:** Observe the dashboard.
    *   **Expected:** "Total XP" should be `15` (assuming a "Perfect" rating, which is default for silent log). "Completed Drills" should be `1`.

3.  **Check History:**
    *   **Action:** Select `7` (📜 Kata History) and press Enter.
    *   **Expected:**
        *   A table titled "📜 Kata History" appears.
        *   It contains one entry: `Python Warmup` with the date and notes "Tests passed (Watch Mode Auto-Log)".

4.  **Resume Last Kata:**
    *   **Action:** Press Enter to return to the menu.
    *   **Action:** Select `3` (▶️ Resume Last Kata (python-warmup-xxx)) and press Enter.
    *   **Expected:**
        *   The "📝 SITREP" panel appears with "Last Log: Tests passed..."
        *   It asks "Launch training environment now? [y/n]". Type `y` and Enter.
        *   The environment (`nvim` + `dojo watch`) launches again.

---
**This complete walkthrough ensures every major feature we implemented is working as intended for a brand new user.**
