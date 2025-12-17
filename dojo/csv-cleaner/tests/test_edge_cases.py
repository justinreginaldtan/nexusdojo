import csv
import tempfile
from pathlib import Path
import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_drops_rows_missing_required_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "out.csv"
            rows = [
                ["id", "email"],
                ["1", "user@example.com"],
                ["2", ""],  # missing email
            ]
            with input_path.open("w", newline="") as f:
                csv.writer(f).writerows(rows)

            stats = main.clean_csv(input_path, output_path, ["id", "email"])
            self.assertEqual(stats["total_rows"], 2)
            self.assertEqual(stats["dropped_rows"], 1)

            with output_path.open() as f:
                cleaned = list(csv.reader(f))
            self.assertEqual(cleaned, [["id", "email"], ["1", "user@example.com"]])

    def test_missing_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.csv"
            with self.assertRaises(FileNotFoundError):
                main.clean_csv(missing, missing, ["id"])
