"""Tests for Binary Search."""
import unittest
import main


class BSTests(unittest.TestCase):
    def test_search(self) -> None:
        self.assertEqual(main.binary_search([-1,0,3,5,9,12], 9), 4)
        self.assertEqual(main.binary_search([-1,0,3,5,9,12], 2), -1)


if __name__ == '__main__':
    unittest.main()
