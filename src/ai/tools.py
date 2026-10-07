from typing import Callable, Dict, Any, List
from src.services.weather import WeatherService
from src.services.news import NewsService
from src.services.wikipedia_service import WikipediaService
from src.services.jokes import JokeService
from src.services.task_manager import TaskManager
from src.services.scheduler import ReminderScheduler

class ToolRegistry:
    def __init__(
        self,
        weather_service: WeatherService = None,
        news_service: NewsService = None,
        wiki_service: WikipediaService = None,
        joke_service: JokeService = None,
        task_manager: TaskManager = None,
        scheduler: ReminderScheduler = None
    ):
        self.weather_service = weather_service or WeatherService()
        self.news_service = news_service or NewsService()
        self.wiki_service = wiki_service or WikipediaService()
        self.joke_service = joke_service or JokeService()
        self.task_manager = task_manager or TaskManager()
        self.scheduler = scheduler or ReminderScheduler()

    def get_tool_functions(self) -> List[Callable]:
        return [
            self.get_weather,
            self.get_news,
            self.search_wikipedia,
            self.tell_joke,
            self.add_task,
            self.list_tasks,
            self.set_reminder
        ]

    def get_weather(self, city: str = "London") -> str:
        """Get current weather information for a specified city."""
        return self.weather_service.get_weather(city)

    def get_news(self, topic: str = "general") -> str:
        """Get top news headlines for a specified topic."""
        return self.news_service.get_top_headlines(topic)

    def search_wikipedia(self, query: str) -> str:
        """Search Wikipedia for a summary of a person, place, or topic."""
        return self.wiki_service.search_summary(query)

    def tell_joke(self) -> str:
        """Tell a funny programming or general joke."""
        return self.joke_service.get_joke()

    def add_task(self, task: str) -> str:
        """Add a new task to the user's personal task list."""
        return self.task_manager.add_task(task)

    def list_tasks(self) -> str:
        """List all active tasks in the user's task list."""
        return self.task_manager.list_tasks()

    def set_reminder(self, text: str, seconds: int) -> str:
        """Set a proactive reminder timer with text description and duration in seconds."""
        return self.scheduler.schedule_reminder(text, seconds)
