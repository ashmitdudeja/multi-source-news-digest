import httpx
from server.config import settings


GUARDIAN_BASE = "https://content.guardianapis.com"


async def fetch_from_guardian() -> list[dict]:
    """
    Fetch latest articles from The Guardian's Content API.
    Requests full body text and thumbnails.
    Normalizes into unified article format.
    """
    if not settings.guardian_api_key:
        print("[Guardian] No API key configured, skipping")
        return []

    all_articles = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            url = f"{GUARDIAN_BASE}/search"
            params = {
                "api-key": settings.guardian_api_key,
                "show-fields": "bodyText,thumbnail,byline",
                "page-size": 30,
                "order-by": "newest",
            }
            response = await client.get(url, params=params)

            if response.status_code != 200:
                print(f"[Guardian] HTTP {response.status_code}")
                return []

            data = response.json()
            results = data.get("response", {}).get("results", [])

            for article in results:
                if not article.get("webTitle") or not article.get("webUrl"):
                    continue

                fields = article.get("fields", {})
                body_text = fields.get("bodyText", "")

                all_articles.append({
                    "source": "The Guardian",
                    "source_id": article.get("id", ""),
                    "title": article["webTitle"],
                    "description": body_text[:300] if body_text else "",
                    "content": body_text,
                    "url": article["webUrl"],
                    "image_url": fields.get("thumbnail"),
                    "author": fields.get("byline", "The Guardian"),
                    "published_at": article.get("webPublicationDate", ""),
                })

            print(f"[Guardian] Fetched {len(all_articles)} articles")

        except Exception as e:
            print(f"[Guardian] Error: {e}")

    return all_articles
