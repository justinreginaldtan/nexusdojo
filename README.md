# NexusDojo: The AI Solutions Engineer's Gym

> *"Mastery through repetition."*

NexusDojo is a local-first CLI designed to train you in **Python**, **APIs**, and **AI Engineering** patterns. It transforms your terminal into a "Zen Dojo" where you can practice coding katas with zero friction, guided by an AI Sensei.

## 🚀 Features

*   **⚡ Quick Train (Magic Button):** One-click session start. The AI analyzes your weakest skills and auto-generates a targeted kata.
*   **🤖 Sensei Check:** Automated test runner that provides AI-powered diagnosis for failures.
*   **👀 Watch Mode:** A file watcher that auto-runs tests on save. Perfect for Neovim/Vim workflows.
*   **📜 Spec-Driven Development:** Every kata starts with a generated `MISSION.md`, simulating a real-world engineering ticket with Requirements, Inputs, Outputs, and Constraints.
*   **🧩 Templates:**
    *   `script`: General Python logic and data processing.
    *   `fastapi`: Building REST APIs.
    *   `rag`: Retrieval-Augmented Generation pipelines (ChromaDB stubs).
    *   `mcp`: Micro-Capability Protocol servers for Agentic tools.

## 📈 Progression System

The Dojo tracks your growth across 4 pillars: **Python**, **CLI**, **API**, and **Testing**.
*   **XP:** Earn XP by completing katas.
*   **Levels:** Novice → Apprentice → Journeyman → Expert → Master.
*   **Adaptation:** As you level up, the `Quick Train` AI will generate harder challenges to keep you in the flow state.

## 🛠️ Setup

1.  Create a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```
2.  Install dependencies (including `rich` and `watchdog`):
    ```bash
    pip install -e .
    ```

## 🥋 The Recommended Workflow

**Goal:** Frictionless training loop.

1.  **Enter the Dojo:**
    ```bash
    dojo menu
    ```
    Select **[1] Quick Train** to instantly generate a challenge based on your skill gaps.

2.  **Understand the Mission:**
    Go to the created directory:
    ```bash
    cd dojo/<kata-slug>
    cat MISSION.md
    ```
    Read the **Goal**, **Inputs**, **Outputs**, and **Acceptance Criteria**.

3.  **Enter "Sensei Watch Mode":**
    Open a terminal pane (or tmux split) and run:
    ```bash
    dojo watch
    ```
    This will sit quietly and wait for you to save files.

4.  **Code (The Vibe):**
    Open `main.py` in your editor (Neovim recommended).
    *   Implement the logic.
    *   Save the file (`:w`).
    *   Look at the "Watch" pane.
        *   **🔴 Red:** Read the error. If stuck, the AI will auto-diagnose the traceback.
        *   **🟢 Green:** "MISSION COMPLETE".

5.  **Log & Archive:**
    Once passed, run:
    ```bash
    dojo log <kata-slug> --note "Learned about list comprehensions"
    ```

## 📚 Commands Reference

| Command | Description |
| :--- | :--- |
| `dojo menu` | Interactive, premium dashboard to control everything. |
| `dojo check` | Run tests once. If fail, get AI hint. If pass, celebrate. |
| `dojo watch` | Continuously run `dojo check` on file save. |
| `dojo start` | Manually start a kata (if you don't use Quick Train). |
| `dojo hint` | Ask the AI for a hint (Unlimited usage). |
| `dojo info` | View environment stats. |

## 🏗️ Architecture

*   **Core:** Python `argparse` CLI.
*   **UI:** `rich` for panels, colors, and tables.
*   **AI:** `ollama` (local) or `openrouter` (cloud) for generating ideas, specs, and hints.
*   **Testing:** Standard `unittest` library wrapped in custom runners.

## 🔮 Roadmap

*   **Phase 1 (Foundation):** Python Mastery & CLI (Current).
*   **Phase 2 (Architect):** RAG & MCP Templates (Ready).
*   **Phase 3 (Engineer):** Agentic workflows and tool use.

---
*Built for the Engineer who builds the future.*