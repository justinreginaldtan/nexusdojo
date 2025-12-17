"""Tests for Rotate Image."""
import unittest
import main


class RotateTests(unittest.TestCase):
    def test_rotate(self) -> None:
        m = [[1,2,3],[4,5,6],[7,8,9]]
        main.rotate(m)
        self.assertEqual(m, [[7,4,1],[8,5,2],[9,6,3]])


if __name__ == '__main__':
    unittest.main()
