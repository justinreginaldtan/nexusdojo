import unittest

from main import calculate_age


class MissionTests(unittest.TestCase):
    def test_returns_age(self) -> None:
        self.assertEqual(calculate_age(2000, 2025), 25)
        self.assertEqual(calculate_age(2025, 2025), 0)

    def test_rejects_future_birth_year(self) -> None:
        with self.assertRaises(ValueError):
            calculate_age(2030, 2025)


if __name__ == "__main__":
    unittest.main()
