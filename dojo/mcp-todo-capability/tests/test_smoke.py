"""Functional smoke tests for MCP Todo Capability server."""

import unittest

from fastapi.testclient import TestClient
import main


class MCPTodoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(main.app)

    def test_tools_endpoint(self) -> None:
        resp = self.client.get("/tools")
        self.assertEqual(resp.status_code, 200)
        tools = resp.json()
        self.assertIsInstance(tools, list)
        self.assertTrue(any(t.get("name") == "list_todos" for t in tools))

    def test_execute_tool_create_and_list(self) -> None:
        created = self.client.post(
            "/execute_tool",
            json={"tool_name": "create_todo", "tool_args": {"title": "test item", "tags": ["dev"]}},
        )
        self.assertEqual(created.status_code, 200)
        cid = created.json().get("result", {}).get("id")
        self.assertIsNotNone(cid)
        listed = self.client.post("/execute_tool", json={"tool_name": "list_todos", "tool_args": {}})
        self.assertEqual(listed.status_code, 200)
        todos = listed.json().get("result", [])
        self.assertTrue(any(t["id"] == cid for t in todos))

    def test_execute_tool_invalid(self) -> None:
        resp = self.client.post("/execute_tool", json={"tool_name": "unknown", "tool_args": {}})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
