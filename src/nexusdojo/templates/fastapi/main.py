# --- SECTION 1: IMPORTS & SETUP ---
# Everything lives in this file so you can see the full FastAPI flow end-to-end.
from fastapi import FastAPI

# Initializes the FastAPI web server with a descriptive title.
app = FastAPI(title="{{IDEA}}")


# --- SECTION 2: YOUR LOGIC (Write Code Here) ---
@app.get("/health")
def health() -> dict[str, str]:
    """Lightweight readiness probe; returns 200 when the app is healthy."""
    return {"status": "ok", "template": "fastapi"}


@app.get("/echo")
def echo(message: str) -> dict[str, str]:
    """
    Echo back a query parameter to verify request handling.
    Add more routes like this as you build out your API.
    """
    return {"echo": message}


# --- SECTION 3: THE ENGINE (Don't Touch Yet) ---
if __name__ == "__main__":
    # Run a local development server with autoreload so code changes take effect.
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
