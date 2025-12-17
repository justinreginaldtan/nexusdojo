import unittest
import main


def build_list(values):
    head = None
    for val in reversed(values):
        head = main.ListNode(val, head)
    return head


class EdgeCases(unittest.TestCase):
    def test_palindrome_true(self) -> None:
        head = build_list([1, 2, 2, 1])
        self.assertTrue(main.is_palindrome(head))

    def test_palindrome_false(self) -> None:
        head = build_list([1, 2])
        self.assertFalse(main.is_palindrome(head))

    def test_empty_list(self) -> None:
        self.assertTrue(main.is_palindrome(None))
