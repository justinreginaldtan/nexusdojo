# NexusDojo: The Engineering Flight Simulator

**Master the muscle memory of shipping AI tooling (Python + RAG + MCP).**

NexusDojo is not a bootcamp. It is a local CLI "gym" that forces you to write code, run tests, and debug in a real environment (Neovim/Tmux). It removes the friction of "what do I build?" so you can focus on "how do I build it?"

## 📍 The Plan
- Overall roadmap: `ROADMAP.md`
- 2-week execution sprint: `14_DAY_SPRINT.md`

## 🎯 The Core Philosophy
1.  **The Gym (Drills):** Small, isolated problems (Katas) to build syntax fluency.
2.  **The Workshop (Projects):** Blank-canvas builds to practice architecture.
3.  **Turbo Feedback:** A sub-second "Red/Green" test runner (`dojo watch`) that keeps you in the flow state.

## 🚀 Quickstart

1.  **Enter the Dojo:**
    ```bash
    dojo menu
    ```
    If `dojo` isn't on your PATH, run `./.venv/bin/dojo menu` (or `source .venv/bin/activate` first).
2.  **Select Your Arena:**
    *   **[1] The Gym:** Choose "Golden Path" for a curated curriculum (Python Basics -> OOP).
3.  **Code:**
    *   The system opens **Neovim** (Left) and **Turbo Watch** (Right).
    *   Edit `main.py`. Save. Watch the tests pass instantly.

## 🛠️ The Stack
*   **CLI:** Python + Argparse (The engine).
*   **TUI:** Rich (The visuals).
*   **Testing:** Unittest (The judge).
*   **Environment:** Local `.venv`, acting as a sandbox.

## 🥋 The Golden Path (Phase 1)
A 7-step progression to clear the rust and build a foundation:
1.  **Hello Personalized World:** Functions & Strings.
2.  **Age Calculator:** Basic Math & Integers.
3.  **Temp Converter:** Control Flow (If/Else).
4.  **Log File Cleaner:** Lists & Loops.
5.  **Password Validator:** Boolean Logic & Iteration.
6.  **Inventory Aggregator:** Dictionaries (Hash Maps).
7.  **Todo Class:** Object Oriented Programming (OOP).

## ⚡ Turbo Mode
We intentionally disabled the slow "AI Agent" features in the CLI.
*   **Dojo Watch:** Runs raw python tests. < 200ms feedback.
*   **Diagnosis:** If you are stuck, copy the error and ask your **Senior Mentor (Gemini)** in the chat. Don't wait for a local model to think.

---
*Built by Justin Tan. Powered by Discipline.*
