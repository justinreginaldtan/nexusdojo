"""Behavioral tests for FAQ Retriever."""

import unittest

import main


class FAQTests(unittest.TestCase):
    def test_retrieve_and_answer(self) -> None:
        self.assertTrue(hasattr(main, "retrieve_context"))
        self.assertTrue(hasattr(main, "generate_response"))
        context = main.retrieve_context("reset password", k=3)
        self.assertIsInstance(context, list)
        self.assertLessEqual(len(context), 3)
        answer = main.generate_response("How do I reset my password?", context)
        self.assertIsInstance(answer, str)
        self.assertTrue(answer)


if __name__ == "__main__":
    unittest.main()
