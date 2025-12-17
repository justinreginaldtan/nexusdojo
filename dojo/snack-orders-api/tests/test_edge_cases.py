import unittest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


class EdgeCases(unittest.TestCase):
    def test_health(self) -> None:
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")

    def test_order_lifecycle_and_stats(self) -> None:
        create = client.post("/orders", json={"customer": "Sam", "snack": "Chips", "quantity": 2})
        self.assertEqual(create.status_code, 201)
        order = create.json()
        order_id = order.get("id")
        self.assertIsNotNone(order_id)

        listed = client.get("/orders").json()
        self.assertEqual(len(listed), 1)

        patched = client.patch(f"/orders/{order_id}", json={"status": "ready"})
        self.assertEqual(patched.json().get("status"), "ready")

        stats = client.get("/stats").json()
        self.assertGreaterEqual(stats.get("total_orders", 0), 1)
        self.assertIn("ready", stats.get("by_status", {}))
