"""Palindrome Linked List stub."""
from __future__ import annotations
from typing import Optional

class ListNode:
    def __init__(self, val: int, next: Optional['ListNode']=None):
        self.val = val
        self.next = next

def is_palindrome(head: Optional[ListNode]) -> bool:
    raise NotImplementedError("Implement is_palindrome")

def main() -> None:
    n1 = ListNode(1, ListNode(2, ListNode(2, ListNode(1))))
    print(is_palindrome(n1))

if __name__ == "__main__":
    main()
