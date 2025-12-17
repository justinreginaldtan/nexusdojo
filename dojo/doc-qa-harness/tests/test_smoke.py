"""Behavioral tests for Doc QA Harness."""

import unittest

import main


class DocQATests(unittest.TestCase):
    def test_retrieve_and_answer(self) -> None:
        self.assertTrue(hasattr(main, "retrieve"))
        self.assertTrue(hasattr(main, "answer"))
        hits = main.retrieve("refund policy", k=3)
        self.assertIsInstance(hits, list)
        self.assertLessEqual(len(hits), 3)
        response = main.answer("What is the refund policy?")
        self.assertIsInstance(response, dict)
        self.assertIn("answer", response)
        self.assertIn("sources", response)


if __name__ == "__main__":
    unittest.main()
