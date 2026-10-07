import requests

class WikipediaService:
    def search_summary(self, query: str) -> str:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "")
                if extract:
                    return f"Wikipedia summary for '{query}':\n{extract}"
        except Exception as e:
            print(f"[WikipediaService] Error querying Wikipedia: {e}")

        return f"No Wikipedia entry found for '{query}'."
