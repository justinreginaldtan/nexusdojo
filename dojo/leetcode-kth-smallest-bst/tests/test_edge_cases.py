import unittest
import main


def build_bst() -> main.TreeNode:
    #       5
    #      / \
    #     3   7
    #    / \   \
    #   2   4   8
    return main.TreeNode(
        5,
        main.TreeNode(3, main.TreeNode(2), main.TreeNode(4)),
        main.TreeNode(7, None, main.TreeNode(8)),
    )


class EdgeCases(unittest.TestCase):
    def test_kth_elements(self) -> None:
        root = build_bst()
        self.assertEqual(main.kth_smallest(root, 1), 2)
        self.assertEqual(main.kth_smallest(root, 3), 4)
        self.assertEqual(main.kth_smallest(root, 5), 7)

    def test_out_of_range_k_raises(self) -> None:
        root = build_bst()
        with self.assertRaises(ValueError):
            main.kth_smallest(root, 0)
        with self.assertRaises(ValueError):
            main.kth_smallest(root, 10)
