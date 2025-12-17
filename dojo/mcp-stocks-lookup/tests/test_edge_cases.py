import unittest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


class EdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        main.STOCKS = {
            "AAPL": {"symbol": "AAPL", "price": 150.0, "currency": "USD", "change": 1.23},
            "MSFT": {"symbol": "MSFT", "price": 300.5, "currency": "USD", "change": -0.5},
        }

    def test_health_and_tools(self) -> None:
        self.assertEqual(client.get("/health").status_code, 200)
        tools = client.get("/tools").json()
        names = {t["name"] for t in tools}
        self.assertIn("quote", names)

    def test_quote_happy_path(self) -> None:
        resp = client.post("/execute_tool", json={"tool_name": "quote", "tool_args": {"symbol": "AAPL"}})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("result", body)
        self.assertEqual(body["result"]["symbol"], "AAPL")

    def test_unknown_symbol_returns_error(self) -> None:
        resp = client.post("/execute_tool", json={"tool_name": "quote", "tool_args": {"symbol": "ZZZZ"}})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("error", body)
