import requests
import xml.etree.ElementTree as ET
from src.config import NEWS_API_KEY

class NewsService:
    def get_top_headlines(self, topic: str = "general") -> str:
        # 1. Try NewsAPI if key available
        if NEWS_API_KEY and NEWS_API_KEY != "your_news_api_key_here":
            try:
                url = f"https://newsapi.org/v2/top-headlines?category={topic}&language=en&apiKey={NEWS_API_KEY}"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    articles = resp.json().get("articles", [])[:3]
                    if articles:
                        lines = [f"- {a['title']}" for a in articles]
                        return f"Top headlines for {topic}:\n" + "\n".join(lines)
            except Exception as e:
                print(f"[NewsService] NewsAPI error: {e}")

        # 2. Fallback to BBC RSS feeds
        try:
            url = "http://feeds.bbci.co.uk/news/rss.xml"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                items = root.findall("./channel/item")[:3]
                titles = [f"- {item.find('title').text}" for item in items if item.find("title") is not None]
                if titles:
                    return "Top BBC News Headlines:\n" + "\n".join(titles)
        except Exception as e:
            print(f"[NewsService] RSS error: {e}")

        return "Unable to retrieve top news headlines at the moment."
