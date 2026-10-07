import logging
from typing import Dict, Any, Callable

from src.services.weather import get_weather
from src.services.news import get_news
from src.services.wikipedia_service import search_wikipedia
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

# 3. Wikipedia Tool
def tool_search_wikipedia(query: str) -> str:
    """Search Wikipedia for a short 2-sentence summary about a topic, person, or concept."""
    return search_wikipedia(query)

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


# Function Registry Mapping for Gemini Function Calling Execution
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_weather": tool_get_weather,
    "get_news": tool_get_news,
    "search_wikipedia": tool_search_wikipedia,
    "add_task": tool_add_task,
    "get_tasks": tool_get_tasks,
    "clear_tasks": tool_clear_tasks,
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
        "name": "search_wikipedia",
        "description": "Search Wikipedia for summaries about people, places, or concepts.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search topic or entity name"}
            },
            "required": ["query"]
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
    }
]
