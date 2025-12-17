"""Tests for Word Ladder Length."""
import unittest
import main


class LadderTests(unittest.TestCase):
    def test_length(self) -> None:
        self.assertEqual(main.ladder_length("hit", "cog", ["hot","dot","dog","lot","log","cog"]), 5)
        self.assertEqual(main.ladder_length("hit", "cog", ["hot","dot","dog","lot","log"]), 0)


if __name__ == '__main__':
    unittest.main()
