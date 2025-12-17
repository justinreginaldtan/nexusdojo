"""Functional smoke tests for Snack Orders API."""

import unittest

from fastapi.testclient import TestClient
import main


class SnackOrdersTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(main.app)

    def test_health(self) -> None:
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")

    def test_create_and_list_order(self) -> None:
        payload = {"customer": "alex", "snack": "chips", "quantity": 2}
        created = self.client.post("/orders", json=payload)
        self.assertEqual(created.status_code, 201)
        body = created.json()
        self.assertIsInstance(body.get("id"), int)
        self.assertEqual(body["customer"], "alex")
        # List and ensure it shows up
        listed = self.client.get("/orders").json()
        self.assertTrue(any(o["id"] == body["id"] for o in listed))

    def test_status_update_and_stats(self) -> None:
        payload = {"customer": "sam", "snack": "candy", "quantity": 1}
        created = self.client.post("/orders", json=payload).json()
        oid = created["id"]
        updated = self.client.patch(f"/orders/{oid}", json={"status": "ready"})
        self.assertEqual(updated.status_code, 200)
        stats = self.client.get("/stats")
        self.assertEqual(stats.status_code, 200)
        data = stats.json()
        self.assertIn("counts", data)
        self.assertIsInstance(data["counts"], dict)
        self.assertIn("ready", data["counts"])


if __name__ == "__main__":
    unittest.main()
