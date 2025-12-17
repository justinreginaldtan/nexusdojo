import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_parse_input_trims_whitespace(self) -> None:
        op, a, b = main.parse_input("  add   4   6 ")
        self.assertEqual(op, "add")
        self.assertEqual((a, b), (4.0, 6.0))

    def test_parse_input_requires_three_tokens(self) -> None:
        with self.assertRaises(ValueError):
            main.parse_input("")
        with self.assertRaises(ValueError):
            main.parse_input("add only-two")

    def test_division_precision(self) -> None:
        op, a, b = main.parse_input("div 1 3")
        self.assertAlmostEqual(main.calculate(op, a, b), 1/3, places=6)
