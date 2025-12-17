import unittest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


class EdgeCases(unittest.TestCase):
    def test_health(self) -> None:
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")

    def test_tool_listing(self) -> None:
        resp = client.get("/tools")
        self.assertEqual(resp.status_code, 200)
        tools = resp.json()
        names = {t["name"] for t in tools}
        self.assertIn("create_todo", names)
        self.assertIn("list_todos", names)

    def test_create_list_complete_delete_flow(self) -> None:
        create = client.post("/execute_tool", json={"tool_name": "create_todo", "tool_args": {"title": "Test todo"}})
        self.assertEqual(create.status_code, 200)
        todo = create.json().get("result")
        todo_id = todo.get("id")
        self.assertIsNotNone(todo_id)

        listed = client.post("/execute_tool", json={"tool_name": "list_todos", "tool_args": {}}).json()["result"]
        self.assertEqual(len(listed), 1)

        complete = client.post("/execute_tool", json={"tool_name": "complete_todo", "tool_args": {"id": todo_id}})
        self.assertEqual(complete.json()["result"]["status"], "completed")

        delete = client.post("/execute_tool", json={"tool_name": "delete_todo", "tool_args": {"id": todo_id}})
        self.assertTrue(delete.json()["result"])

        listed_after = client.post("/execute_tool", json={"tool_name": "list_todos", "tool_args": {}}).json()["result"]
        self.assertEqual(listed_after, [])
