"""Functional smoke tests for JWT Notes API."""

import unittest

from fastapi.testclient import TestClient
import main


class JwtNotesTests(unittest.TestCase):
    def setUp(self) -> None:
        main.USERS.clear()
        main.NOTES.clear()
        self.client = TestClient(main.app)

    def test_signup_login_me_flow(self) -> None:
        # Signup
        signup = self.client.post("/auth/signup", json={"email": "a@example.com", "password": "secret123"})
        self.assertEqual(signup.status_code, 201)
        # Login
        login = self.client.post("/auth/login", json={"email": "a@example.com", "password": "secret123"})
        self.assertEqual(login.status_code, 200)
        token = login.json().get("access_token")
        self.assertTrue(token)
        headers = {"Authorization": f"Bearer {token}"}
        me = self.client.get("/me", headers=headers)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json().get("email"), "a@example.com")

    def test_notes_are_scoped_to_user(self) -> None:
        # User A
        self.client.post("/auth/signup", json={"email": "a@example.com", "password": "aaa"})
        a_token = self.client.post("/auth/login", json={"email": "a@example.com", "password": "aaa"}).json()["access_token"]
        # User B
        self.client.post("/auth/signup", json={"email": "b@example.com", "password": "bbb"})
        b_token = self.client.post("/auth/login", json={"email": "b@example.com", "password": "bbb"}).json()["access_token"]
        # A creates a note
        a_headers = {"Authorization": f"Bearer {a_token}"}
        created = self.client.post("/notes", json={"title": "A note"}, headers=a_headers)
        self.assertEqual(created.status_code, 201)
        # B should not see A's note
        b_headers = {"Authorization": f"Bearer {b_token}"}
        notes_b = self.client.get("/notes", headers=b_headers).json()
        self.assertEqual(notes_b, [])


if __name__ == "__main__":
    unittest.main()
