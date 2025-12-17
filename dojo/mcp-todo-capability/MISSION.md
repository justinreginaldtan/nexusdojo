# MCP Todo Capability Server

Expose todo operations as micro-capabilities over FastAPI, suitable for MCP-style tool calling.

## Setup
- Install kata deps: `pip install -r requirements.txt`
- Run tests: `python -m unittest`

## Requirements
- Endpoints: `/health` (GET), `/execute_tool` (POST) that accepts `{ "tool_name": str, "tool_args": {...} }`.
- Supported tools: `list_todos`, `create_todo(title, tags?)`, `complete_todo(id)`, `delete_todo(id)`, `summary()`.
- Maintain todos in memory with ids, status, title, optional tags, created_at.
- Validate tool args and return structured `{ "result": ..., "error": ... }` with HTTP 200.
- Include a `/tools` endpoint that returns schema/metadata for available tools (names, args, descriptions).

## Stretch
- Add persistence to a JSON file.
- Add filtering (by tag/status) for `list_todos`.
