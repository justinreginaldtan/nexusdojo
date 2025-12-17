# Chain-of-Thought Calculator (LangChain)

Build a LangChain pipeline that handles natural language math prompts, routes to a calculator tool, and returns JSON-structured answers.

## Requirements
- Implement a simple calculator tool (add, subtract, multiply, divide with error handling).
- Create a LangChain chain that: (1) rewrites user prompts into clear operations, (2) calls the tool, (3) returns `{ "result": number, "reasoning": "..." }`.
- Add input validation and guard against unsupported operations.
- Provide a small CLI entry point: `python main.py "What is 3.5 times 8?"` -> prints JSON.

## Stretch
- Add a router that detects non-math prompts and returns a friendly refusal message.
- Keep a short in-memory trace of the last 5 calls and expose via a flag (`--history`).
