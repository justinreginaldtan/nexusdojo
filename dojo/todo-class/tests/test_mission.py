import unittest

from main import Todo


class MissionTests(unittest.TestCase):
    def test_starts_empty(self) -> None:
        todo = Todo()
        self.assertEqual(todo.get_tasks(), [])

    def test_adds_tasks_in_order(self) -> None:
        todo = Todo()
        todo.add("a")
        todo.add("b")
        self.assertEqual(todo.get_tasks(), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
