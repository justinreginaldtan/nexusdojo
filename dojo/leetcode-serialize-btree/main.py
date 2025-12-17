"""Serialize/Deserialize Binary Tree stub."""
from __future__ import annotations
from typing import Optional

class TreeNode:
    def __init__(self, val: int, left: Optional['TreeNode']=None, right: Optional['TreeNode']=None):
        self.val = val
        self.left = left
        self.right = right

class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        raise NotImplementedError("Implement serialize")
    def deserialize(self, data: str) -> Optional[TreeNode]:
        raise NotImplementedError("Implement deserialize")

def main() -> None:
    root = TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))
    codec = Codec()
    s = codec.serialize(root)
    print(s)

if __name__ == "__main__":
    main()
