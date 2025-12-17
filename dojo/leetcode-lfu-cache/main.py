"""LFU Cache stub."""
from __future__ import annotations

class LFUCache:
    def __init__(self, capacity: int):
        raise NotImplementedError
    def get(self, key: int) -> int:
        raise NotImplementedError
    def put(self, key: int, value: int) -> None:
        raise NotImplementedError

def main() -> None:
    cache = LFUCache(2)
    cache.put(1,1)
    print(cache.get(1))

if __name__ == "__main__":
    main()
