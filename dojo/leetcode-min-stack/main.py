"""Min Stack stub."""
from __future__ import annotations

class MinStack:
    def __init__(self):
        raise NotImplementedError
    def push(self, val: int) -> None:
        raise NotImplementedError
    def pop(self) -> None:
        raise NotImplementedError
    def top(self) -> int:
        raise NotImplementedError
    def get_min(self) -> int:
        raise NotImplementedError

def main() -> None:
    ms = MinStack()
    print(ms)

if __name__ == "__main__":
    main()
