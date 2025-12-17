import unittest
import main


BOARD = [
    ["o","a","a","n"],
    ["e","t","a","e"],
    ["i","h","k","r"],
    ["i","f","l","v"],
]


class EdgeCases(unittest.TestCase):
    def test_finds_words(self) -> None:
        words = ["oath","pea","eat","rain"]
        found = main.find_words([row[:] for row in BOARD], words)
        self.assertEqual(set(found), {"oath", "eat"})

    def test_no_matches(self) -> None:
        found = main.find_words([row[:] for row in BOARD], ["zzz"])
        self.assertEqual(found, [])
