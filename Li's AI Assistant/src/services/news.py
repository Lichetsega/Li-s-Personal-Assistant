import os
import sys
import requests
import xml.etree.ElementTree as ET
import logging

# Ensure root project path is included in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.config import config

logger = logging.getLogger("NewsService")

def get_news(limit: int = 5) -> str:
    """
    Fetch top news headlines.
    Uses NewsAPI if API key is set, otherwise falls back to RSS feed.
    """
    api_key = config.NEWS_API_KEY
    if api_key:
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize={limit}&apiKey={api_key}"
            res = requests.get(url, timeout=5)
            data = res.json()
            if data.get("status") == "ok":
                articles = data.get("articles", [])[:limit]
                headlines = [f"{i+1}. {art['title']}" for i, art in enumerate(articles)]
                return "Here are the top news headlines:\n" + "\n".join(headlines)
        except Exception as e:
            logger.warning(f"NewsAPI failed: {e}. Trying fallback...")

    # Fallback to BBC RSS feed
    try:
        url = "http://feeds.bbci.co.uk/news/rss.xml"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            headlines = []
            for i, item in enumerate(root.findall(".//item")[:limit]):
                title = item.find("title").text
                headlines.append(f"{i+1}. {title}")
            return "Here are the top headlines from BBC News:\n" + "\n".join(headlines)
    except Exception as e:
        logger.error(f"RSS News fallback failed: {e}")

    return "Sorry, I couldn't fetch news updates right now."
