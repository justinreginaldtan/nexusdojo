"""Tests for Palindrome Linked List."""
import unittest
import main


class PalListTests(unittest.TestCase):
    def build(self, vals):
        head = None
        for v in reversed(vals):
            head = main.ListNode(v, head)
        return head

    def test_palindrome(self) -> None:
        self.assertTrue(main.is_palindrome(self.build([1,2,2,1])))
        self.assertFalse(main.is_palindrome(self.build([1,2])))


if __name__ == '__main__':
    unittest.main()
