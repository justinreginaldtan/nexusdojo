import unittest

from main import convert_temp


class MissionTests(unittest.TestCase):
    def test_celsius_to_fahrenheit(self) -> None:
        self.assertAlmostEqual(convert_temp(0, "C"), 32.0, places=6)
        self.assertAlmostEqual(convert_temp(100, "C"), 212.0, places=6)

    def test_fahrenheit_to_celsius(self) -> None:
        self.assertAlmostEqual(convert_temp(32, "F"), 0.0, places=6)
        self.assertAlmostEqual(convert_temp(212, "F"), 100.0, places=6)

    def test_invalid_scale_raises(self) -> None:
        with self.assertRaises(ValueError):
            convert_temp(10, "K")


if __name__ == "__main__":
    unittest.main()
