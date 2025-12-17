import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_groups_anagrams(self) -> None:
        res = main.group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
        normalized = {frozenset(group) for group in map(tuple, res)}
        self.assertIn(frozenset(["eat", "tea", "ate"]), normalized)
        self.assertIn(frozenset(["tan", "nat"]), normalized)
        self.assertIn(frozenset(["bat"]), normalized)

    def test_empty_input(self) -> None:
        self.assertEqual(main.group_anagrams([]), [])
