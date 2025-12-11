# Changelog

All notable changes to the NexusDojo project will be documented in this file.

## [Unreleased] - 2025-12-11

### 🚀 Major Features (The "Zen" Upgrade)
*   **Zen Terminal UI:** Replaced raw text output with the `rich` library. The CLI now features a premium, dashboard-style interface with panels, colors, and interactive menus.
*   **Progression System (XP):** Added a gamified skill tracking system.
    *   Tracks XP across 4 pillars: Python, API, CLI, Testing.
    *   **Levels:** Novice -> Apprentice -> Journeyman -> Expert -> Master.
    *   **Adaptive Difficulty:** `Quick Train` now generates harder/easier katas based on your current Level.
*   **Sensei Check (`dojo check`):**
    *   Automated test runner that provides instant visual feedback (Green/Red panels).
    *   **AI Diagnosis:** On failure, the AI analyzes the traceback and provides a specific logic hint.
*   **Watch Mode (`dojo watch`):**
    *   File watcher using `watchdog`. Auto-runs `dojo check` on file save. Optimized for Neovim workflows.
*   **Spec-Driven Development:**
    *   `dojo start` now uses an LLM to generate a `MISSION.md`.
    *   This file acts as a "Ticket," defining Inputs, Outputs, and Constraints (e.g., "Must handle errors").
*   **New Templates:**
    *   `rag`: Stub for Retrieval-Augmented Generation pipelines.
    *   `mcp`: Stub for Micro-Capability Protocol servers (FastAPI).

### ⚡ Improvements
*   **Unlimited Hints:** Removed the daily cap on hints. Reduced cooldown to 5 seconds (debounce only).
*   **Quick Train:** Added a "Magic Button" to the main menu that auto-selects the weakest skill and launches a training session instantly.

### 🐛 Fixes
*   Fixed `handle_start` to correctly generate metadata (`.kata.json`) for XP tracking.
*   Standardized `main.py` stubs for non-script templates to avoid empty files.
