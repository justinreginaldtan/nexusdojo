"""MCP Todo capability server stub."""
from __future__ import annotations
from typing import Any
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/tools")
def tools() -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/execute_tool")
def execute_tool(payload: Any) -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")


def main() -> None:
    print("Implement FastAPI app exposing MCP-style tools.")

if __name__ == "__main__":
    main()
