import unittest

from main import aggregate_inventory


class MissionTests(unittest.TestCase):
    def test_counts_items(self) -> None:
        items = ["apple", "apple", "banana"]
        self.assertEqual(aggregate_inventory(items), {"apple": 2, "banana": 1})

    def test_empty_list(self) -> None:
        self.assertEqual(aggregate_inventory([]), {})


if __name__ == "__main__":
    unittest.main()
