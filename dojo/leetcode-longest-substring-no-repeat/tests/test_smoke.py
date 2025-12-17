"""Tests for Longest Substring Without Repeating Characters."""
import unittest
import main


class LongestSubstrTests(unittest.TestCase):
    def test_length(self) -> None:
        self.assertEqual(main.length_of_longest_substring("abcabcbb"), 3)
        self.assertEqual(main.length_of_longest_substring("bbbbb"), 1)
        self.assertEqual(main.length_of_longest_substring("pwwkew"), 3)


if __name__ == '__main__':
    unittest.main()
