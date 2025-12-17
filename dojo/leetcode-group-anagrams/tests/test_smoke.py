"""Tests for Group Anagrams."""
import unittest
import main


class GroupTests(unittest.TestCase):
    def test_groups(self) -> None:
        res = main.group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
        groups = [sorted(g) for g in res]
        self.assertIn(sorted(["eat", "tea", "ate"]), groups)
        self.assertIn(sorted(["tan", "nat"]), groups)
        self.assertIn(["bat"], groups)


if __name__ == '__main__':
    unittest.main()
