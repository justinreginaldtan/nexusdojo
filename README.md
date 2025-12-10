# NexusDojo CLI (Branch A)

Local-first command-line dojo for practicing Python/CLI/API skills with tiny katas. The CLI entrypoint is `dojo`.

## Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install in editable mode (exposes the `dojo` command):
   ```bash
   python3 -m pip install -e .
   ```

## Usage
- Show help and commands:
  ```bash
  dojo --help
  ```
- Print a quickstart reminder:
  ```bash
  dojo hello
  ```
- Ask the idea picker to propose katas. Defaults to local Ollama (no API key needed) with `llama3.2:1b`:
  ```bash
  dojo idea
  ```
  Ensure the Ollama daemon is running and the model is pulled (e.g., `ollama pull llama3.2:1b`).
  To use OpenRouter instead, set `NEXUSDOJO_API_KEY` and run:
  ```bash
  dojo idea --provider openrouter --model google/gemini-2.0-flash-001
  ```
- Create a kata from a template (default: script; also: fastapi):
  ```bash
  # If you omit the idea, `dojo start` will call the idea picker.
  dojo start "My Idea" --template fastapi
  ```
- Log what you did for a kata:
  ```bash
  dojo log my-idea --note "Implemented echo endpoint"
  ```
- Summarize recent logs and write a brief:
  ```bash
  dojo brief --since 2025-01-01
  ```
- Record a quick calibration (1-5) for a pillar:
  ```bash
  dojo calibrate --pillar api --score 3 --note "Need more error handling practice"
  ```
- Show the mentor system prompt (or any prompt file):
  ```bash
  dojo prompt --file system_prompts/senior_ai_mentor.md
  ```
- Inspect environment info:
  ```bash
  dojo info
  ```
- Create a local workspace skeleton for knowledge artifacts:
  ```bash
  dojo init --path ./nexusdojo_data
  ```
  Add `--force` to reuse a non-empty directory.
- Build an API payload without sending it (demonstrates env vars):
  ```bash
  export NEXUSDOJO_API_KEY=sk-...
  dojo api-dry-run --provider openai --message "Hello"
  ```

## Development
- Run tests:
  ```bash
  python3 -m unittest
  ```
- Code lives under `src/nexusdojo`. Entry point is `nexusdojo/cli.py`.
- Templates live under `templates/` (script, fastapi). Kata output root defaults to `./dojo/`. Notes and briefs default to `./notes/`.

## Next steps
- Add more templates (RAG stub, MCP server skeleton) once the core loop feels solid.
- Layer prompts/agent workflows using the MCP protocol to coordinate tools (later).
