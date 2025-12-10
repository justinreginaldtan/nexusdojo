"""
Starter FastAPI app for a NexusDojo kata.
"""

from fastapi import FastAPI

app = FastAPI(title="{{IDEA}}")


@app.get("/health")
def health() -> dict[str, str]:
    """
    Lightweight readiness probe.
    """
    return {"status": "ok", "template": "fastapi"}


@app.get("/echo")
def echo(message: str) -> dict[str, str]:
    """
    Echo back a query parameter to verify request handling.
    """
    return {"echo": message}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
