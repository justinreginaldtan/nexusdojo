import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_examples(self) -> None:
        self.assertEqual(main.trap([0,1,0,2,1,0,1,3,2,1,2,1]), 6)
        self.assertEqual(main.trap([4,2,0,3,2,5]), 9)
