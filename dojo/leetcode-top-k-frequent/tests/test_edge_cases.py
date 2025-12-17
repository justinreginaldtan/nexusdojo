import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_top_k(self) -> None:
        res = main.top_k_frequent([1,1,1,2,2,3], 2)
        self.assertEqual(set(res), {1, 2})

    def test_single_element(self) -> None:
        self.assertEqual(main.top_k_frequent([1], 1), [1])
