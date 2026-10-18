"""
GitHub Integration Service for Li's Personal Assistant.
Fetches live repository stats, recent commits, and README specifications
directly from GitHub (https://github.com/Lichetsega) with in-memory caching.
"""

import time
import json
import logging
import urllib.request
import urllib.error
import base64
from typing import Dict, Any, Optional, List

logger = logging.getLogger("GitHubService")

GITHUB_USERNAME = "Lichetsega"
CACHE_TTL_SECONDS = 900  # 15 minutes cache to avoid rate limits

_cache: Dict[str, Dict[str, Any]] = {}

def _fetch_github_api(endpoint: str) -> Optional[Any]:
    """Helper to fetch GitHub REST API with caching and error handling."""
    now = time.time()
    if endpoint in _cache:
        cached_entry = _cache[endpoint]
        if now - cached_entry["timestamp"] < CACHE_TTL_SECONDS:
            return cached_entry["data"]

    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Li-Personal-Assistant/2.0",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                _cache[endpoint] = {"timestamp": now, "data": data}
                return data
    except urllib.error.HTTPError as e:
        logger.warning(f"GitHub API HTTP error {e.code} on {endpoint}: {e.reason}")
    except Exception as e:
        logger.warning(f"GitHub API request failed on {endpoint}: {e}")
    return None

def list_user_repos() -> str:
    """List public repositories with stars, language, and descriptions."""
    data = _fetch_github_api(f"users/{GITHUB_USERNAME}/repos?sort=updated&per_page=10")
    if not data or not isinstance(data, list):
        return (
            "Li's key featured repositories on GitHub (https://github.com/Lichetsega):\n"
            "• Li-s-Personal-Assistant (Voice AI assistant with FastAPI & Gemini)\n"
            "• Agentic-Retrieval-Augmented-Generation-Agentic-RAG- (Visit Ethiopia Multi-Agent System)\n"
            "• password_checker (SHA-1 k-Anonymity breach auditor)\n"
            "• hacker_news-scraper (High-signal Python news aggregator)"
        )

    lines = [f"Li's Public Repositories (GitHub: @{GITHUB_USERNAME}):"]
    for r in data[:6]:
        name = r.get("name", "")
        desc = r.get("description") or "No description provided."
        lang = r.get("language") or "Code"
        url = r.get("html_url", "")
        lines.append(f"• **{name}** ({lang}): {desc} [Link: {url}]")
    return "\n".join(lines)

def get_latest_commits(repo_name: str, count: int = 3) -> str:
    """Fetch the latest commits for a specific repository."""
    # Clean repo name
    clean_name = repo_name.strip().strip("/").replace("Lichetsega/", "")
    data = _fetch_github_api(f"repos/{GITHUB_USERNAME}/{clean_name}/commits?per_page={count}")
    if not data or not isinstance(data, list):
        return f"Could not retrieve recent commits for '{clean_name}'. Please visit https://github.com/{GITHUB_USERNAME}/{clean_name} to view the commit history."

    lines = [f"Latest commits on `{clean_name}`:"]
    for c in data[:count]:
        commit_info = c.get("commit", {})
        msg = commit_info.get("message", "").split("\n")[0]
        date_str = commit_info.get("author", {}).get("date", "")[:10]
        sha = c.get("sha", "")[:7]
        lines.append(f"• [{sha}] ({date_str}) {msg}")
    return "\n".join(lines)

def get_repo_readme_summary(repo_name: str) -> str:
    """Fetch and summarize a repository's README."""
    clean_name = repo_name.strip().strip("/").replace("Lichetsega/", "")
    data = _fetch_github_api(f"repos/{GITHUB_USERNAME}/{clean_name}/readme")
    if not data or "content" not in data:
        return f"Could not fetch README for '{clean_name}'. Check the repository at https://github.com/{GITHUB_USERNAME}/{clean_name}."

    try:
        raw_text = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        # Extract first 600 characters or clean summary
        summary = raw_text.strip()[:650]
        return f"README overview for `{clean_name}`:\n{summary}..."
    except Exception as e:
        logger.error(f"Error decoding README for {clean_name}: {e}")
        return f"README for `{clean_name}` is available at https://github.com/{GITHUB_USERNAME}/{clean_name}"
