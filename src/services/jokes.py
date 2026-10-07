import random

class JokeService:
    JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "There are 10 types of people in the world: those who understand binary, and those who don't.",
        "Why did the Python developer need glasses? Because they couldn't C#!",
        "An SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
        "How many programmers does it take to change a lightbulb? None, that's a hardware problem!"
    ]

    def get_joke(self) -> str:
        return random.choice(self.JOKES)
