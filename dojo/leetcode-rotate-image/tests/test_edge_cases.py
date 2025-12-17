import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_rotate_3x3(self) -> None:
        matrix = [[1,2,3],[4,5,6],[7,8,9]]
        main.rotate(matrix)
        self.assertEqual(matrix, [[7,4,1],[8,5,2],[9,6,3]])

    def test_rotate_2x2(self) -> None:
        matrix = [[1,2],[3,4]]
        main.rotate(matrix)
        self.assertEqual(matrix, [[3,1],[4,2]])
