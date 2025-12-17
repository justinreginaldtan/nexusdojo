"""Word Ladder stub."""
from __future__ import annotations
from typing import List

def ladder_length(begin_word: str, end_word: str, word_list: List[str]) -> int:
    raise NotImplementedError("Implement ladder_length")

def main() -> None:
    print(ladder_length("hit", "cog", ["hot","dot","dog","lot","log","cog"]))

if __name__ == "__main__":
    main()
