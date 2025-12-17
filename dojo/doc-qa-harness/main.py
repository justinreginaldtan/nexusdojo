"""Doc QA harness stub."""
from __future__ import annotations
from typing import List, Dict

def retrieve(query: str, k: int = 3) -> List[Dict[str, str]]:
    raise NotImplementedError("Implement retrieve")

def answer(query: str) -> Dict[str, object]:
    raise NotImplementedError("Implement answer")

def main() -> None:
    print("Implement retrieve()/answer() plus eval harness.")

if __name__ == "__main__":
    main()
