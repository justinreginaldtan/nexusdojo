import unittest

from main import clean_errors


class MissionTests(unittest.TestCase):
    def test_filters_and_strips(self) -> None:
        lines = [" ERROR: fail ", "INFO: ok", "ERROR: disk full", " WARNING "]
        self.assertEqual(clean_errors(lines), ["ERROR: fail", "ERROR: disk full"])

    def test_no_errors(self) -> None:
        self.assertEqual(clean_errors(["INFO: ok", "DEBUG: x"]), [])


if __name__ == "__main__":
    unittest.main()
