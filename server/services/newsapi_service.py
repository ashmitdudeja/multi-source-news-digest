import httpx
from server.config import settings


NEWSAPI_BASE = "https://newsapi.org/v2"


async def fetch_from_newsapi() -> list[dict]:
    """
    Fetch top headlines from NewsAPI.org across multiple categories.
    Normalizes response into unified article format.
    """
    if not settings.newsapi_key:
        print("[NewsAPI] No API key configured, skipping")
        return []

    all_articles = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for category in settings.newsapi_categories:
            try:
                url = f"{NEWSAPI_BASE}/top-headlines"
                params = {
                    "country": "us",
                    "category": category,
                    "pageSize": 20,
                    "apiKey": settings.newsapi_key,
                }
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    print(f"[NewsAPI] HTTP {response.status_code} for category '{category}'")
                    continue

                data = response.json()

                if data.get("status") != "ok" or not data.get("articles"):
                    print(f"[NewsAPI] Bad response for '{category}': {data.get('message', 'unknown')}")
                    continue

                count = 0
                for article in data["articles"]:
                    # Skip removed/unavailable articles
                    if not article.get("title") or article["title"] == "[Removed]":
                        continue
                    if not article.get("url"):
                        continue

                    all_articles.append({
                        "source": "NewsAPI",
                        "source_id": f"newsapi-{hash(article['url']) & 0xFFFFFFFF}",
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "content": article.get("content") or article.get("description", ""),
                        "url": article["url"],
                        "image_url": article.get("urlToImage"),
                        "author": article.get("author") or (article.get("source", {}).get("name", "Unknown")),
                        "published_at": article.get("publishedAt", ""),
                    })
                    count += 1

                print(f"[NewsAPI] Fetched {count} articles for '{category}'")

            except Exception as e:
                print(f"[NewsAPI] Error fetching '{category}': {e}")

    return all_articles
