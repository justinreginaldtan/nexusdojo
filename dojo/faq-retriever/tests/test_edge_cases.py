"""Edge cases and acceptance coverage for FAQ Retriever."""
import unittest
import main


class EdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        main.FAQS = [
            {"question": "How do I reset my password?", "answer": "Click reset on the login page."},
            {"question": "How to update billing info?", "answer": "Go to billing settings."},
            {"question": "Where are invoices stored?", "answer": "Invoices live under billing."},
        ]

    def test_retrieve_top_k(self) -> None:
        results = main.retrieve_context("reset password", k=2)
        self.assertLessEqual(len(results), 2)
        self.assertEqual(results[0]["question"], "How do I reset my password?")

    def test_generate_response_includes_answers(self) -> None:
        ctx = [
            {"question": "How do I reset my password?", "answer": "Click reset on the login page."},
            {"question": "How to update billing info?", "answer": "Go to billing settings."},
        ]
        reply = main.generate_response("reset password", ctx)
        self.assertIsInstance(reply, str)
        self.assertIn("Click reset on the login page.", reply)
        self.assertIn("billing", reply)
