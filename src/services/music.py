import webbrowser
import logging

logger = logging.getLogger("MusicService")

def play_music(topic: str) -> str:
    """
    Search and play music on YouTube using standard webbrowser.
    """
    if not topic or not topic.strip():
        topic = "popular music"

    try:
        url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
        logger.info(f"Opening YouTube for '{topic}'...")
        webbrowser.open(url)
        return f"Playing {topic} on YouTube."
    except Exception as ex:
        logger.error(f"Failed to open browser: {ex}")
        return f"Could not play music for {topic}."
