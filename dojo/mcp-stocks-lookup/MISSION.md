# MCP Stocks Lookup Server

Expose a stock quote lookup as an MCP-style tool over FastAPI.

## Setup
- Install kata deps: `pip install -r requirements.txt`
- Run tests: `python -m unittest`

## Requirements
- Endpoints: `/health` (GET), `/tools` (GET metadata), `/execute_tool` (POST) with `{ "tool_name": "quote", "tool_args": {"symbol": "AAPL"} }`.
- Implement a deterministic quote provider (hardcoded or seeded from a JSON file) with fields: symbol, price, change, currency, timestamp.
- Validate symbols (uppercase ticker), return 400-style error objects for bad input, and 404-style errors for unknown symbols.
- Support a simple in-memory cache with TTL to simulate freshness; include cache hit/miss info in responses.
- Return structured JSON with `result` or `error`.

## Stretch
- Add a `history` tool that returns last N quotes for a symbol.
- Add basic rate limiting per client.
