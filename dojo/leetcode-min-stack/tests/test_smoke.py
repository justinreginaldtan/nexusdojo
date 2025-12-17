"""Tests for Min Stack."""
import unittest
import main


class MinStackTests(unittest.TestCase):
    def test_ops(self) -> None:
        ms = main.MinStack()
        ms.push(-2)
        ms.push(0)
        ms.push(-3)
        self.assertEqual(ms.get_min(), -3)
        ms.pop()
        self.assertEqual(ms.top(), 0)
        self.assertEqual(ms.get_min(), -2)


if __name__ == '__main__':
    unittest.main()
