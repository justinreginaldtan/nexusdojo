"""Tests for Valid Parentheses."""
import unittest
import main


class ValidTests(unittest.TestCase):
    def test_samples(self) -> None:
        self.assertTrue(main.is_valid("()[]{}"))
        self.assertFalse(main.is_valid("(]"))
        self.assertFalse(main.is_valid("([)]"))


if __name__ == '__main__':
    unittest.main()
