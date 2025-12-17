"""Kth Smallest BST stub."""
from __future__ import annotations
from typing import Optional

class TreeNode:
    def __init__(self, val: int, left: Optional['TreeNode']=None, right: Optional['TreeNode']=None):
        self.val = val
        self.left = left
        self.right = right

def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    raise NotImplementedError("Implement kth_smallest")

def main() -> None:
    root = TreeNode(3, TreeNode(1, None, None), TreeNode(4, TreeNode(2), None))
    print(kth_smallest(root, 1))

if __name__ == "__main__":
    main()
