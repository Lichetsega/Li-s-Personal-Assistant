import pyjokes
import logging

logger = logging.getLogger("JokesService")

def get_joke(category: str = "neutral") -> str:
    """
    Get a programming or general joke using pyjokes.
    """
    try:
        joke = pyjokes.get_joke(category=category, language="en")
        return joke
    except Exception as e:
        logger.error(f"Error fetching joke: {e}")
        return "Why do programmers prefer dark mode? Because light attracts bugs!"
