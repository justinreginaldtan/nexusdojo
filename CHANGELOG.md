# Changelog

All notable changes to the NexusDojo project will be documented in this file.

## [Unreleased] - 2025-12-11

### 🚀 Major Features (The "Zen" Upgrade & Frictionless Flow)
*   **Context-Aware Menu:** The main menu (`dojo menu`) now dynamically adapts based on your location.
    *   **Lobby Mode:** Shows Start, Resume, Profile, and History when in the project root.
    *   **Kata Mode:** Shows Check, Watch, Hint, Reset, and Solution Reveal when inside a kata directory.
    *   *Why:* Reduces cognitive load by hiding irrelevant options.
*   **Zero-Click Launch:** When starting or resuming a session, the app can automatically launch your coding environment.
    *   **Tmux Support:** Splits the window: Neovim on the left, `dojo watch` on the right.
    *   *Why:* Eliminates the manual setup friction of opening editors and running test watchers.
*   **"Cockpit" Dashboard:** Replaced the text-heavy dashboard with a clean `Grid` layout using `rich`.
    *   **Left:** User Identity & Context.
    *   **Right:** XP, Completed Drills, Consistency Heatmap.
    *   *Why:* Improves scanability of key metrics and current status.
*   **Alive AI Loaders:** Replaced static spinners with multi-step progress indicators for AI operations (Idea Generation, Spec Building).
    *   *Why:* Reduces perceived latency and provides reassurance during long local LLM calls.
*   **Error Panels:** Wrapped `dojo check` failures in styled Red Panels with clear titles.
    *   *Why:* Makes test failures easier to read and distinguishes them from app crashes.

### 📈 Progression System (XP)
*   **Gamified Skill Tracking:** Tracks XP across 4 pillars: Python, CLI, API, Testing.
    *   **Levels:** Novice -> Apprentice -> Journeyman -> Expert -> Master.
    *   **Adaptive Difficulty:** `Quick Train` generates harder/easier katas based on your Level.
*   **Streak Heatmap:** Dashboard displays activity for the last 5 days to encourage consistency.

### 🛠️ Core Improvements
*   **Spec-Driven Development:** `dojo start` generates a `MISSION.md` "ticket" with clear Requirements, Inputs, and Constraints.
*   **Mission Injection:** The Mission spec is automatically injected as a docstring into `main.py`.
*   **Smart Boilerplate:** `main.py` is pre-filled with imports relevant to the mission (e.g., `import json` if JSON parsing is required).
*   **Silent Auto-Log:** Passing tests in Watch Mode logs success automatically without interrupting flow.
*   **Context Restore (Sitrep):** Resuming a session displays the last log entry to help you regain context instantly.
*   **Focus Timer:** `dojo watch` displays a live timer to track session duration.
*   **Dependency Manager:** `dojo check` automatically detects and offers to install missing dependencies from `requirements.txt`.

### 🐛 Fixes & Polish
*   **Path Resolution:** Fixed critical issue where `notes` and `dojo` paths were relative to `cwd`, causing Onboarding loops when running from subdirectories. Now resolves to Repo Root.
*   **Menu Navigation:** Fixed bug where pressing Enter after sub-commands exited the app. Menu now loops correctly.
*   **Timeout Handling:** Increased Ollama/OpenRouter timeouts to 120s to support local inference on older hardware.
*   **New Commands:** Added `dojo play` (Playground), `dojo solve` (Solution Reveal), and `dojo reset` (Clean Slate).

### 🧩 Templates
*   `script`: General Python logic.
*   `fastapi`: Building REST APIs.
*   `rag`: Retrieval-Augmented Generation stub.
*   `mcp`: Micro-Capability Protocol server stub.