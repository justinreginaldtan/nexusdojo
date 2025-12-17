import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_lfu_sequence(self) -> None:
        cache = main.LFUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)  # freq: 1->2, 2->1
        cache.put(3, 3)  # evicts key 2
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(3), 3)
        cache.put(4, 4)  # evicts key 1
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(3), 3)
        self.assertEqual(cache.get(4), 4)
