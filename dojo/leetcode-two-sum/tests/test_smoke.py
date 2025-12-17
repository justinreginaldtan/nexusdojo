"""Tests for Two Sum Variant."""
import unittest
import main


class TwoSumTests(unittest.TestCase):
    def test_two_sum(self) -> None:
        self.assertEqual(sorted(main.two_sum([2,7,11,15], 9)), [0,1])
        self.assertEqual(sorted(main.two_sum([3,2,4], 6)), [1,2])


if __name__ == '__main__':
    unittest.main()
