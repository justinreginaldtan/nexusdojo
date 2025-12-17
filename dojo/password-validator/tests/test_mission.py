import unittest

from main import is_valid_password


class MissionTests(unittest.TestCase):
    def test_valid_password(self) -> None:
        self.assertTrue(is_valid_password("abcd12345"))

    def test_missing_digit(self) -> None:
        self.assertFalse(is_valid_password("thisislong"))

    def test_too_short(self) -> None:
        self.assertFalse(is_valid_password("abc12345"))  # 8 chars


if __name__ == "__main__":
    unittest.main()
