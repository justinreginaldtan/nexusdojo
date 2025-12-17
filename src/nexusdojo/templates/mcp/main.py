# --- SECTION 1: IMPORTS & SETUP ---
# Everything stays in this file so you can see how requests flow to handlers.
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

# Initializes the FastAPI app that will host your micro-capabilities.
app = FastAPI(title="Micro-Capability Protocol Server")


# --- SECTION 2: YOUR LOGIC (Write Code Here) ---
class ToolRequest(BaseModel):
    """Defines the request body for executing a tool via HTTP."""

    tool_name: str
    tool_args: Dict[str, Any]


@app.get("/health")
async def health() -> Dict[str, str]:
    """Basic health endpoint so tests and monitors can check readiness."""
    return {"status": "ok"}


@app.post("/execute_tool")
async def execute_tool(request: ToolRequest) -> Dict[str, Any]:
    """
    Dispatch a requested tool/capability. Add your own tool names and handlers.
    """
    if request.tool_name == "example_tool":
        return {
            "message": f"Executed {request.tool_name} with args: {request.tool_args}"
        }
    return {"error": f"Tool '{request.tool_name}' not found."}


def main() -> None:
    """CLI-friendly entry point so `python main.py` shows a helpful message."""
    print("MCP Server Kata: implement and expose micro-capabilities via HTTP.")
    print("Run tests in 'tests', then start the server with `python main.py`.")


# --- SECTION 3: THE ENGINE (Don't Touch Yet) ---
if __name__ == "__main__":
    # Run a local dev server with autoreload so you can edit routes quickly.
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
