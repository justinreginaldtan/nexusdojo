import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_examples(self) -> None:
        self.assertEqual(main.max_subarray([-2,1,-3,4,-1,2,1,-5,4]), 6)
        self.assertEqual(main.max_subarray([1]), 1)
        self.assertEqual(main.max_subarray([-1, -2]), -1)
