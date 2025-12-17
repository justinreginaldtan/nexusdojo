import unittest
import main


class MissionTests(unittest.TestCase):
    def test_parse_and_calculate_valid_ops(self):
        cases = [
            ("add 2 3", 5.0),
            ("+ -1 4", 3.0),
            ("sub 10 4", 6.0),
            ("mul 2 3.5", 7.0),
            ("div 9 3", 3.0),
            ("/ 7 2", 3.5),
        ]
        for raw, expected in cases:
            op, a, b = main.parse_input(raw)
            self.assertAlmostEqual(main.calculate(op, a, b), expected)

    def test_invalid_numeric_input_raises(self):
        with self.assertRaises(ValueError):
            main.parse_input("add two 3")
        with self.assertRaises(ValueError):
            main.parse_input("add 2 three")

    def test_invalid_shape_or_op(self):
        with self.assertRaises(ValueError):
            main.parse_input("add 2")
        with self.assertRaises(ValueError):
            main.calculate("pow", 2, 3)

    def test_division_by_zero_raises(self):
        op, a, b = main.parse_input("div 10 0")
        with self.assertRaises(ValueError):
            main.calculate(op, a, b)
