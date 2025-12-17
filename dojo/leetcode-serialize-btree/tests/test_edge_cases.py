import unittest
import main
from collections import deque


def bfs_values(root):
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    # trim trailing None noise
    while out and out[-1] is None:
        out.pop()
    return out


class EdgeCases(unittest.TestCase):
    def test_round_trip(self) -> None:
        root = main.TreeNode(1, main.TreeNode(2), main.TreeNode(3, main.TreeNode(4), main.TreeNode(5)))
        codec = main.Codec()
        data = codec.serialize(root)
        rebuilt = codec.deserialize(data)
        self.assertEqual(bfs_values(rebuilt), [1, 2, 3, None, None, 4, 5])

    def test_empty_tree(self) -> None:
        codec = main.Codec()
        data = codec.serialize(None)
        rebuilt = codec.deserialize(data)
        self.assertIsNone(rebuilt)
