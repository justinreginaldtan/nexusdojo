"""Tests for Top K Frequent Elements."""
import unittest
import main


class TopKTests(unittest.TestCase):
    def test_topk(self) -> None:
        res = main.top_k_frequent([1,1,1,2,2,3], 2)
        self.assertEqual(set(res), {1,2})
        res2 = main.top_k_frequent([4,4,4,5,6,6], 1)
        self.assertEqual(res2, [4])


if __name__ == '__main__':
    unittest.main()
