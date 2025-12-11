# Micro-Capability Protocol (MCP) Server Template

This template sets up a basic FastAPI server to expose "micro-capabilities" or "tools" via HTTP endpoints. This is foundational for building AI Agents that use external tools.

## Goal
Implement a new tool within the `execute_tool` endpoint, or refine the existing example tool. The goal is to expose a specific function or capability (e.g., a database lookup, a calculator, a web search) as an API endpoint that an AI agent could call.

## Quickstart
1.  **Implement Logic:** Add your tool logic within the `execute_tool` function in `main.py`.
2.  **Run Tests:** `python -m unittest` in this directory.
3.  **Start Server:** `uvicorn main:app --reload`
4.  **Test Endpoint:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"tool_name": "example_tool", "tool_args": {"query": "hello"}}' http://127.0.0.1:8000/execute_tool
    ```

## Core Concepts
*   **Tooling/Function Calling:** How AI agents interact with external systems.
*   **API Design:** Creating clear, robust interfaces for capabilities.
*   **Decentralized Intelligence:** Breaking down complex problems into smaller, callable services.
