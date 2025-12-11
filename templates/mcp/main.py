from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="Micro-Capability Protocol Server")

class ToolRequest(BaseModel):
    tool_name: str
    tool_args: Dict[str, Any]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/execute_tool")
async def execute_tool(request: ToolRequest):
    """
    Executes a specific tool/capability based on the request.
    TODO: Implement your tools here (e.g., search, calculator, data lookup).
    """
    if request.tool_name == "example_tool":
        # Example tool implementation
        result = {"message": f"Executed {request.tool_name} with args: {request.tool_args}"}
        return result
    else:
        return {"error": f"Tool '{request.tool_name}' not found."}

def main():
    print("MCP Server Kata: Implement and expose micro-capabilities via HTTP.")
    print("Run tests in the 'tests' folder, then `uvicorn main:app --reload`.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
