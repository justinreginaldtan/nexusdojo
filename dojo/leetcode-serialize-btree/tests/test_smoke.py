"""Tests for Serialize/Deserialize Binary Tree."""
import unittest
import main


class CodecTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        root = main.TreeNode(1, main.TreeNode(2), main.TreeNode(3, main.TreeNode(4), main.TreeNode(5)))
        codec = main.Codec()
        data = codec.serialize(root)
        rebuilt = codec.deserialize(data)
        self.assertEqual(codec.serialize(rebuilt), data)


if __name__ == "__main__":
    unittest.main()
