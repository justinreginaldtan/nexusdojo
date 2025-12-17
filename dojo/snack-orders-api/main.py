"""Snack Orders API stub. Implement endpoints per MISSION.md."""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from typing import Any

app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/orders")
def create_order(payload: Any) -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/orders")
def list_orders() -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.patch("/orders/{order_id}")
def update_order(order_id: int, payload: Any) -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/stats")
def stats() -> Any:
    raise HTTPException(status_code=501, detail="Not implemented")


def main() -> None:
    print("Implement FastAPI app and run uvicorn main:app --reload")


if __name__ == "__main__":
    main()
