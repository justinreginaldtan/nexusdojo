import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestAPI(unittest.TestCase):
    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

    def test_echo(self):
        response = client.get("/echo", params={"message": "hi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("echo"), "hi")


if __name__ == "__main__":
    unittest.main()
