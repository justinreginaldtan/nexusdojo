import unittest
from main import sum_numbers

class MissionTests(unittest.TestCase):
    
    def test_1_simple_sum(self):
        """It should sum a list of integers."""
        self.assertEqual(sum_numbers([1, 2, 3]), 6)
        self.assertEqual(sum_numbers([-1, 1]), 0)

    def test_2_empty_list(self):
        """It should return 0 for an empty list."""
        self.assertEqual(sum_numbers([]), 0)

    def test_3_ignore_non_integers(self):
        """It should ignore strings, None, etc."""
        self.assertEqual(sum_numbers([1, "banana", 2, None]), 3)

    def test_4_invalid_input(self):
        """It should raise ValueError if input is not a list."""
        with self.assertRaises(ValueError):
            sum_numbers("not a list")