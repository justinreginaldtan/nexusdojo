"""Behavioral tests for CSV Cleaner CLI."""

import csv
import tempfile
import unittest
from pathlib import Path

import main


class CSVCleanerTests(unittest.TestCase):
    def test_clean_csv_drops_bad_rows(self) -> None:
        self.assertTrue(hasattr(main, "clean_csv"))
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.csv"
            out = Path(tmp) / "clean.csv"
            with raw.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["name", "age"])
                writer.writeheader()
                writer.writerow({"name": "alex", "age": "30"})
                writer.writerow({"name": "", "age": "20"})  # should drop
            summary = main.clean_csv(raw, out, required_columns=["name", "age"])
            self.assertEqual(summary["dropped_rows"], 1)
            rows = list(csv.DictReader(out.open()))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], "alex")


if __name__ == "__main__":
    unittest.main()
