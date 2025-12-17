import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_solution_counts(self) -> None:
        self.assertEqual(main.solve_n_queens(4), 2)
        self.assertEqual(main.solve_n_queens(1), 1)
        self.assertEqual(main.solve_n_queens(2), 0)
        self.assertEqual(main.solve_n_queens(3), 0)
