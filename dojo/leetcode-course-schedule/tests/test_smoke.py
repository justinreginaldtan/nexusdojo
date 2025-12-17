"""Tests for Course Schedule."""
import unittest
import main


class CourseTests(unittest.TestCase):
    def test_can_finish(self) -> None:
        self.assertTrue(main.can_finish(2, [[1,0]]))
        self.assertFalse(main.can_finish(2, [[1,0],[0,1]]))


if __name__ == '__main__':
    unittest.main()
