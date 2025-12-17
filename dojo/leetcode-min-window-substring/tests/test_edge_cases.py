import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_classic_case(self) -> None:
        self.assertEqual(main.min_window("ADOBECODEBANC", "ABC"), "BANC")

    def test_single_char(self) -> None:
        self.assertEqual(main.min_window("a", "a"), "a")

    def test_no_possible_window(self) -> None:
        self.assertEqual(main.min_window("a", "aa"), "")
