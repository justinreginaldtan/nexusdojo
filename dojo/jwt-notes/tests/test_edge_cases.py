import unittest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def signup_and_login(email: str, password: str) -> str:
    resp = client.post("/auth/signup", json={"email": email, "password": password})
    assert resp.status_code in (200, 201)
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token
    return token


class EdgeCases(unittest.TestCase):
    def test_signup_login_and_me(self) -> None:
        token = signup_and_login("user@example.com", "secret123")
        me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me.status_code, 200)
        body = me.json()
        self.assertEqual(body.get("email"), "user@example.com")

    def test_notes_are_isolated_per_user(self) -> None:
        token1 = signup_and_login("a@example.com", "pw1")
        token2 = signup_and_login("b@example.com", "pw2")

        client.post("/notes", json={"content": "note a"}, headers={"Authorization": f"Bearer {token1}"})
        client.post("/notes", json={"content": "note b"}, headers={"Authorization": f"Bearer {token2}"})

        notes_a = client.get("/notes", headers={"Authorization": f"Bearer {token1}"}).json()
        notes_b = client.get("/notes", headers={"Authorization": f"Bearer {token2}"}).json()
        self.assertTrue(all(n["content"] == "note a" for n in notes_a))
        self.assertTrue(all(n["content"] == "note b" for n in notes_b))
