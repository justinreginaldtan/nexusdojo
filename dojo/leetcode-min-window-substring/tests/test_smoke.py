"""Tests for Minimum Window Substring."""
import unittest
import main


class MinWindowTests(unittest.TestCase):
    def test_window(self) -> None:
        self.assertEqual(main.min_window("ADOBECODEBANC", "ABC"), "BANC")
        self.assertEqual(main.min_window("a", "a"), "a")


if __name__ == "__main__":
    unittest.main()
