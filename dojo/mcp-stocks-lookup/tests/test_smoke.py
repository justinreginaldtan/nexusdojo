"""Functional smoke tests for MCP Stocks Lookup server."""

import unittest

from fastapi.testclient import TestClient
import main


class MCPStocksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(main.app)

    def test_tools_endpoint(self) -> None:
        resp = self.client.get("/tools")
        self.assertEqual(resp.status_code, 200)
        tools = resp.json()
        self.assertIsInstance(tools, list)
        self.assertTrue(any(t.get("name") == "quote" for t in tools))

    def test_execute_quote_valid(self) -> None:
        resp = self.client.post("/execute_tool", json={"tool_name": "quote", "tool_args": {"symbol": "AAPL"}})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("result", body)
        result = body["result"]
        self.assertEqual(result.get("symbol"), "AAPL")
        self.assertIn("price", result)

    def test_execute_quote_invalid(self) -> None:
        resp = self.client.post("/execute_tool", json={"tool_name": "quote", "tool_args": {"symbol": "bad"}})
        body = resp.json()
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
