import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_found(self) -> None:
        self.assertEqual(main.binary_search([-1, 0, 3, 5, 9, 12], 9), 4)

    def test_not_found(self) -> None:
        self.assertEqual(main.binary_search([-1, 0, 3, 5, 9, 12], 2), -1)

    def test_single_element(self) -> None:
        self.assertEqual(main.binary_search([1], 1), 0)
        self.assertEqual(main.binary_search([1], 2), -1)
