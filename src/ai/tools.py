import logging
from typing import Dict, Any, Callable

from src.services.weather import get_weather
from src.services.news import get_news
from src.services.task_manager import add_task, get_tasks, clear_tasks

logger = logging.getLogger("GeminiTools")

# 1. Weather Tool
def tool_get_weather(city: str = "London") -> str:
    """Fetch current real-time weather information for a specified city."""
    return get_weather(city)

# 2. News Tool
def tool_get_news(category: str = "general") -> str:
    """Fetch top current news headlines."""
    return get_news(limit=4)

# 4. Task Management Tools
def tool_add_task(task_text: str) -> str:
    """Add a new task or reminder item to Li's task list."""
    return add_task(task_text)

def tool_get_tasks() -> str:
    """List all current active tasks for Li."""
    return get_tasks()

def tool_clear_tasks() -> str:
    """Clear all completed tasks from Li's task list."""
    return clear_tasks()

from src.services.github_service import list_user_repos, get_latest_commits, get_repo_readme_summary

# 5. GitHub Live Inspection Tools
def tool_list_github_repos() -> str:
    """Fetch live list of Li's public repositories from GitHub."""
    return list_user_repos()

def tool_get_github_commits(repo_name: str = "Li-s-Personal-Assistant") -> str:
    """Fetch recent git commits for a specific repository on Li's GitHub."""
    return get_latest_commits(repo_name, count=3)

def tool_get_github_readme(repo_name: str = "Li-s-Personal-Assistant") -> str:
    """Fetch README contents/overview for a specific repository on Li's GitHub."""
    return get_repo_readme_summary(repo_name)


# Function Registry Mapping for Gemini Function Calling Execution
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_weather": tool_get_weather,
    "get_news": tool_get_news,
    "add_task": tool_add_task,
    "get_tasks": tool_get_tasks,
    "clear_tasks": tool_clear_tasks,
    "list_github_repos": tool_list_github_repos,
    "get_github_commits": tool_get_github_commits,
    "get_github_readme": tool_get_github_readme,
}

# Declarative Tool Schema for Google Gemini Function Calling
GEMINI_TOOL_DECLARATIONS = [
    {
        "name": "get_weather",
        "description": "Fetch real-time weather updates for a specified city.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "City name, e.g. London, Tokyo, Paris"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_news",
        "description": "Fetch top current news headlines.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING", "description": "News category e.g. general, technology"}
            }
        }
    },
    {
        "name": "add_task",
        "description": "Add a new task or reminder item to Li's task list.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task_text": {"type": "STRING", "description": "Task description"}
            },
            "required": ["task_text"]
        }
    },
    {
        "name": "get_tasks",
        "description": "Get all current active tasks on Li's task list.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "clear_tasks",
        "description": "Clear all tasks from Li's task list.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "list_github_repos",
        "description": "List Li's latest public code repositories and projects from GitHub (@Lichetsega).",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_github_commits",
        "description": "Fetch the latest git commits for one of Li's repositories (e.g. Li-s-Personal-Assistant, Agentic-Retrieval-Augmented-Generation-Agentic-RAG-, password_checker).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "repo_name": {"type": "STRING", "description": "Repository name, e.g. Li-s-Personal-Assistant or password_checker"}
            },
            "required": ["repo_name"]
        }
    },
    {
        "name": "get_github_readme",
        "description": "Read the README file or specifications for one of Li's GitHub repositories.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "repo_name": {"type": "STRING", "description": "Repository name on GitHub, e.g. password_checker"}
            },
            "required": ["repo_name"]
        }
    }
]
