import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_classic_case(self) -> None:
        length = main.ladder_length("hit", "cog", ["hot","dot","dog","lot","log","cog"])
        self.assertEqual(length, 5)

    def test_no_path_returns_zero(self) -> None:
        length = main.ladder_length("hit", "cog", ["hot","dot","dog","lot","log"])
        self.assertEqual(length, 0)
