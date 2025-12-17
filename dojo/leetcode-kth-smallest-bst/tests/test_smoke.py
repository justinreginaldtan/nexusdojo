"""Tests for Kth Smallest in BST."""
import unittest
import main


class KthTests(unittest.TestCase):
    def build(self):
        return main.TreeNode(3, main.TreeNode(1, None, main.TreeNode(2)), main.TreeNode(4))

    def test_kth(self) -> None:
        root = self.build()
        self.assertEqual(main.kth_smallest(root, 1), 1)
        self.assertEqual(main.kth_smallest(root, 3), 3)


if __name__ == '__main__':
    unittest.main()
