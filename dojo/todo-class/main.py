# --- MISSION.md (synced for quick reference) ---
# # Mission: The Todo Class
# 
# ## Overview
# Create a class `Todo` that stores tasks and exposes:
# - `add(task)` to add a task
# - `get_tasks()` to return the current task list
# 
# ## Rules
# - Store tasks in an instance variable (a list).
# - `add()` appends tasks in order.
# 
# ## Acceptance Criteria (Tests)
# - A new `Todo` starts with no tasks
# - After adding tasks, `get_tasks()` returns them in order
# 
# ## Quickstart
# 1. Read this `MISSION.md`.
# 2. Edit `main.py`.
# 3. Run `dojo watch`.

from __future__ import annotations


class Todo:
    def __init__(self) -> None:
        # TODO: Initialize your task storage.
        self._tasks: list[str] = []

    def add(self, task: str) -> None:
        """Add a task to the list."""
        # TODO: Implement.
        pass

    def get_tasks(self) -> list[str]:
        """Return the current tasks in order."""
        # TODO: Implement.
        return []


def main() -> None:
    todo = Todo()
    todo.add("Ship")
    todo.add("Apply")
    print(todo.get_tasks())


if __name__ == "__main__":
    main()
