import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestMCPServer(unittest.TestCase):
    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_execute_tool_example_tool(self):
        response = client.post(
            "/execute_tool",
            json={"tool_name": "example_tool", "tool_args": {"input": "test"}}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Executed example_tool", response.json()["message"])

    def test_execute_tool_unknown_tool(self):
        response = client.post(
            "/execute_tool",
            json={"tool_name": "unknown_tool", "tool_args": {}}
        )
        self.assertEqual(response.status_code, 200) # FastAPI returns 200 for custom error responses
        self.assertIn("Tool 'unknown_tool' not found.", response.json()["error"])

    @unittest.skip("Implement this test: Test a new tool with specific inputs and outputs.")
    def test_execute_tool_new_tool_logic(self):
        pass
