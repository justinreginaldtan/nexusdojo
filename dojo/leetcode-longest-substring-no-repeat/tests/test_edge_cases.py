import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_examples(self) -> None:
        self.assertEqual(main.length_of_longest_substring("abcabcbb"), 3)
        self.assertEqual(main.length_of_longest_substring("bbbbb"), 1)
        self.assertEqual(main.length_of_longest_substring("pwwkew"), 3)

    def test_empty_string(self) -> None:
        self.assertEqual(main.length_of_longest_substring(""), 0)
