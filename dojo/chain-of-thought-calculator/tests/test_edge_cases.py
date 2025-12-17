import unittest
import main


class EdgeCases(unittest.TestCase):
    def test_simple_addition(self) -> None:
        resp = main.process_prompt("What is 2 plus 3?")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp.get("result"), 5)
        self.assertIsInstance(resp.get("reasoning"), str)

    def test_division(self) -> None:
        resp = main.process_prompt("compute 10 divided by 2")
        self.assertEqual(resp.get("result"), 5)
        self.assertIsInstance(resp.get("reasoning"), str)

    def test_unsupported_operation(self) -> None:
        with self.assertRaises(ValueError):
            main.process_prompt("tell me a joke")
