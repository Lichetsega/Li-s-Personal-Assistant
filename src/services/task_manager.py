from typing import List

class TaskManager:
    def __init__(self):
        self.tasks: List[str] = []

    def add_task(self, task: str) -> str:
        task_str = task.strip()
        if task_str:
            self.tasks.append(task_str)
            return f"Task added: '{task_str}'."
        return "Task content cannot be empty."

    def list_tasks(self) -> str:
        if not self.tasks:
            return "You have no active tasks right now."
        return "Your active tasks:\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(self.tasks)])

    def clear_tasks(self) -> str:
        count = len(self.tasks)
        self.tasks.clear()
        return f"Cleared {count} tasks."
