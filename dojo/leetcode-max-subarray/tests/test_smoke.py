"""Tests for Max Subarray."""
import unittest
import main


class MaxSubarrayTests(unittest.TestCase):
    def test_max(self) -> None:
        self.assertEqual(main.max_subarray([-2,1,-3,4,-1,2,1,-5,4]), 6)
        self.assertEqual(main.max_subarray([1]), 1)


if __name__ == '__main__':
    unittest.main()
