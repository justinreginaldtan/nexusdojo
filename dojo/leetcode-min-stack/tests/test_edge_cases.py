import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_min_stack_ops(self) -> None:
        stack = main.MinStack()
        stack.push(-2)
        stack.push(0)
        stack.push(-3)
        self.assertEqual(stack.get_min(), -3)
        stack.pop()
        self.assertEqual(stack.top(), 0)
        self.assertEqual(stack.get_min(), -2)
