# NexusDojo: The Roadmap Alignment Strategy

This document maps the features of the NexusDojo CLI directly to your goal of becoming an **AI Solutions Engineer**.

## Phase 1: The Foundation (Weeks 1-4)
**Goal:** Muscle memory for Python, CLI comfort, and "Vibe Coding."

*   **Roadmap Requirement:** "Comfort in the terminal. Writing code that runs."
*   **Dojo Feature: `dojo menu` -> Quick Train (Magic Button)**
    *   **How it helps:** Removes decision fatigue. You hit `1`, you get a task, you code. It builds the daily habit.
*   **Roadmap Requirement:** "Just-In-Time Fundamentals."
    *   **Dojo Feature: Adaptive Difficulty**
    *   **How it helps:** The AI sees you are a "Novice" in Python. It gives you "Foundation" drills (loops, lists) until you level up. It prevents you from tackling complex APIs before you know basic syntax.
*   **Roadmap Requirement:** "Neovim workflow."
    *   **Dojo Feature: `dojo watch`**
    *   **How it helps:** Keeps your hands on the keyboard. No alt-tabbing to run tests.

## Phase 2: The Architect (Weeks 5-8)
**Goal:** RAG, Data, and MCP Basics. "Understanding how to feed Context."

*   **Roadmap Requirement:** "Build a simple, local MCP Server."
    *   **Dojo Feature: Template `mcp`**
    *   **How it helps:** `dojo start --template mcp` generates a FastAPI stub pre-configured for Tool Use. You focus on the logic, not the boilerplate.
*   **Roadmap Requirement:** "Naive RAG pipelines."
    *   **Dojo Feature: Template `rag`**
    *   **How it helps:** `dojo start --template rag` gives you a `retrieve_context` function stub. It forces you to think about "Retrieval" and "Generation" as separate engineering steps.

## Phase 3: The Engineer (Weeks 9-12)
**Goal:** Agents, Logic, and Robustness.

*   **Roadmap Requirement:** "Error Handling (`try/except`)."
    *   **Dojo Feature: `MISSION.md` (Constraints)**
    *   **How it helps:** The generated mission explicitly demands constraints like "Handle File Not Found errors." You aren't just writing happy-path code; you are engineering robust solutions.
*   **Roadmap Requirement:** "Building systems that 'think' and 'act'."
    *   **Dojo Feature: `dojo check` (Sensei Diagnosis)**
    *   **How it helps:** When your complex Agent logic fails, the AI Sensei analyzes the traceback and explains *why* the logic broke. This builds your debugging intuition.

## Phase 4: The Professional (Weeks 13-16)
**Goal:** Shipping and Portfolio.

*   **Roadmap Requirement:** "Polish the Resume/LinkedIn."
    *   **Dojo Feature: XP & Progression System**
    *   **How it helps:** You have concrete data. "I reached Level 4 (Expert) in API Design in 3 months." This is a powerful story for interviews.
*   **Roadmap Requirement:** "Active Vibe Coding (Explain the code)."
    *   **Dojo Feature: `MISSION.md`**
    *   **How it helps:** You are training to read a spec and implement it. This is exactly what a Senior Engineer expects from a Junior/Mid-level hire.
