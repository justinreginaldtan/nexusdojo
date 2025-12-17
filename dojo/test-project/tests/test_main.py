"""Auto-generated tests for the FastAPI scaffold. Edit as needed."""
import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class ScaffoldTests(unittest.TestCase):
    def test_health_exists(self) -> None:
        resp = client.get('/health')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), dict)
