import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_can_finish_true_and_false(self) -> None:
        self.assertTrue(main.can_finish(2, [[1, 0]]))
        self.assertFalse(main.can_finish(2, [[1, 0], [0, 1]]))
