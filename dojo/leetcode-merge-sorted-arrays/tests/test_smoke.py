"""Tests for Merge Sorted Arrays."""
import unittest
import main


class MergeTests(unittest.TestCase):
    def test_merge(self) -> None:
        self.assertEqual(main.merge([1,3,5],[2,4]), [1,2,3,4,5])
        self.assertEqual(main.merge([], [1]), [1])


if __name__ == '__main__':
    unittest.main()
