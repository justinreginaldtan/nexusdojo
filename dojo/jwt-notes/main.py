"""JWT Notes API stub. Implement auth + notes per MISSION.md."""
from __future__ import annotations
from typing import Any
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/auth/signup")
def signup(payload: Any) -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/auth/login")
def login(payload: Any) -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/me")
def me() -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/notes")
def list_notes() -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/notes")
def create_note(payload: Any) -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")


def main() -> None:
    print("Implement FastAPI app and run uvicorn main:app --reload")


if __name__ == "__main__":
    main()
