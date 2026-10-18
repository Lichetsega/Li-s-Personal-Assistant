import datetime
import logging

logger = logging.getLogger("TaskManager")

_tasks = []

def add_task(task_description: str) -> str:
    """Add a new task to memory."""
    if not task_description:
        return "Please specify a task to add."
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    _tasks.append({"task": task_description, "created_at": timestamp})
    return f"Added task: '{task_description}'."

def get_tasks() -> str:
    """Retrieve current task list."""
    if not _tasks:
        return "You currently have no pending tasks."
    result = "Here are your tasks:\n"
    for i, t in enumerate(_tasks, 1):
        result += f"{i}. {t['task']} (Added: {t['created_at']})\n"
    return result.strip()

def clear_tasks() -> str:
    """Clear all tasks."""
    _tasks.clear()
    return "All tasks have been cleared."
