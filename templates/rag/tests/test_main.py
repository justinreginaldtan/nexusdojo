import unittest
from main import retrieve_context, generate_response

class TestRAG(unittest.TestCase):
    def test_retrieve_context_returns_list_of_strings(self):
        query = "What is the capital of France?"
        context = retrieve_context(query)
        self.assertIsInstance(context, list)
        for item in context:
            self.assertIsInstance(item, str)

    def test_generate_response_returns_string(self):
        query = "What is the capital of France?"
        context = ["Paris is the capital of France."]
        response = generate_response(query, context)
        self.assertIsInstance(response, str)
        self.assertIn("Paris", response)

    @unittest.skip("Implement this test: Test retrieve_context with no results.")
    def test_retrieve_context_no_results(self):
        pass

    @unittest.skip("Implement this test: Test generate_response with empty context.")
    def test_generate_response_empty_context(self):
        pass
