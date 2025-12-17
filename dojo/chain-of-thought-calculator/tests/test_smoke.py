"""Behavioral tests for Chain-of-Thought Calculator."""

import unittest

import main


class CalculatorChainTests(unittest.TestCase):
    def test_basic_multiplication(self) -> None:
        self.assertTrue(hasattr(main, "process_prompt"))
        result = main.process_prompt("What is 3 times 4?")
        self.assertIsInstance(result, dict)
        self.assertIn("result", result)
        self.assertIn("reasoning", result)
        self.assertEqual(result["result"], 12)

    def test_reject_non_math(self) -> None:
        result = main.process_prompt("Tell me a joke.")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
