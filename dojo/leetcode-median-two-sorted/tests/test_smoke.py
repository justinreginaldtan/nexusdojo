"""Tests for Median of Two Sorted Arrays."""
import unittest
import main


class MedianTests(unittest.TestCase):
    def test_median(self) -> None:
        self.assertEqual(main.find_median_sorted_arrays([1, 3], [2]), 2.0)
        self.assertEqual(main.find_median_sorted_arrays([1, 2], [3, 4]), 2.5)


if __name__ == "__main__":
    unittest.main()
