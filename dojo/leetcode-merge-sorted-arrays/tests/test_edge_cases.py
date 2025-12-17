import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_merge_sorted_lists(self) -> None:
        self.assertEqual(main.merge([1, 3, 5], [2, 4]), [1, 2, 3, 4, 5])

    def test_with_empty_lists(self) -> None:
        self.assertEqual(main.merge([], [1, 2]), [1, 2])
        self.assertEqual(main.merge([1, 2], []), [1, 2])
