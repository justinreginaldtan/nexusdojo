"""Course Schedule stub."""
from __future__ import annotations
from typing import List

def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:
    raise NotImplementedError("Implement can_finish")

def main() -> None:
    print(can_finish(2, [[1,0]]))

if __name__ == "__main__":
    main()
