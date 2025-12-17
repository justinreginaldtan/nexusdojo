"""Edge cases and acceptance coverage for Doc QA Harness."""
import unittest
import main


class EdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        main.DOCS = [
            {"title": "Install", "text": "To install, run pip install ."},
            {"title": "Usage", "text": "To use the tool, run cli --help"},
        ]

    def test_retrieve_top_match(self) -> None:
        ctx = main.retrieve("install instructions", k=1)
        self.assertEqual(len(ctx), 1)
        self.assertIn("Install", ctx[0]["title"])

    def test_answer_includes_snippet(self) -> None:
        result = main.answer("How do I install?")
        self.assertIsInstance(result, dict)
        self.assertIn("Install", result.get("source", ""))
        self.assertIsInstance(result.get("answer"), str)
