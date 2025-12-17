import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_examples(self) -> None:
        self.assertTrue(main.is_valid("()"))
        self.assertTrue(main.is_valid("()[]{}"))
        self.assertFalse(main.is_valid("(]"))
        self.assertFalse(main.is_valid("([)]"))
        self.assertFalse(main.is_valid("{"))
