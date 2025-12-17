"""Tests for Word Search II."""
import unittest
import main


class WordSearchTests(unittest.TestCase):
    def test_words(self) -> None:
        board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
        res = main.find_words(board, ["oath","pea","eat","rain"])
        self.assertEqual(set(res), {"oath", "eat"})


if __name__ == "__main__":
    unittest.main()
