import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_basic_example(self) -> None:
        self.assertEqual(sorted(main.two_sum([2, 7, 11, 15], 9)), [0, 1])

    def test_with_duplicates(self) -> None:
        self.assertEqual(sorted(main.two_sum([3, 3, 4, 5], 6)), [0, 1])

    def test_no_solution_raises(self) -> None:
        with self.assertRaises(ValueError):
            main.two_sum([1, 2, 3], 7)
