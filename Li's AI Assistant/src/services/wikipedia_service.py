import requests
import logging

logger = logging.getLogger("WikipediaService")

def search_wikipedia(query: str, sentences: int = 2) -> str:
    """
    Search Wikipedia for a summary of the query topic.
    Uses Wikipedia's REST API via standard requests (no extra library required).
    """
    if not query or not query.strip():
        return "Please provide a topic to search on Wikipedia."

    clean_query = query.strip().replace(" ", "_")
    
    # 1. Try official Wikipedia REST API endpoint
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query}"
        headers = {"User-Agent": "LiVoiceAssistant/1.0 (contact@example.com)"}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            extract = data.get("extract", "")
            if extract:
                lines = extract.split(". ")
                short_summary = ". ".join(lines[:sentences])
                if not short_summary.endswith("."):
                    short_summary += "."
                return f"According to Wikipedia: {short_summary}"
    except Exception as e:
        logger.warning(f"Wikipedia REST API lookup failed: {e}. Trying search endpoint...")

    # 2. Fallback to Wikipedia Opensearch endpoint for broader search terms
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&format=json"
        res = requests.get(search_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if len(data) >= 3 and data[2]:
                extract = data[2][0]
                if extract:
                    return f"According to Wikipedia: {extract}"
    except Exception as e:
        logger.error(f"Wikipedia search fallback failed: {e}")

    return f"Sorry, I couldn't find any Wikipedia article matching '{query}'."

