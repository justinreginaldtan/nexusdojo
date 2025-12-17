"""Tests for N-Queens."""
import unittest
import main


class NQueenTests(unittest.TestCase):
    def test_count(self) -> None:
        self.assertEqual(main.solve_n_queens(4), 2)
        self.assertEqual(main.solve_n_queens(1), 1)


if __name__ == "__main__":
    unittest.main()
