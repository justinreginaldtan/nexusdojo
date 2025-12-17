"""Word Search II stub."""
from __future__ import annotations
from typing import List

def find_words(board: List[List[str]], words: List[str]) -> List[str]:
    raise NotImplementedError("Implement find_words")

def main() -> None:
    board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
    print(find_words(board, ["oath","pea","eat","rain"]))

if __name__ == "__main__":
    main()
