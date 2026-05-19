import feedparser
from server.config import settings


async def fetch_from_rss() -> list[dict]:
    """
    Parse RSS feeds from BBC News and Reuters using feedparser.
    Uses HTTPS URLs only (BBC's HTTP endpoint silently redirects and can fail).
    Normalizes RSS entries into unified article format.
    """
    all_articles = []

    for feed_config in settings.rss_feeds:
        feed_name = feed_config["name"]
        feed_url = feed_config["url"]

        try:
            # feedparser is synchronous but lightweight — acceptable for RSS parsing
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                print(f"[RSS] Failed to parse feed '{feed_name}': {feed.bozo_exception}")
                continue

            count = 0
            for entry in feed.entries:
                title = entry.get("title", "")
                link = entry.get("link", "")

                if not title or not link:
                    continue

                # Extract description from summary or content
                description = ""
                if entry.get("summary"):
                    description = entry.summary
                elif entry.get("content"):
                    description = entry.content[0].get("value", "")

                # Strip HTML tags from description
                import re
                description = re.sub(r"<[^>]+>", "", description).strip()

                # Extract image from media content or enclosures
                image_url = None
                if entry.get("media_thumbnail"):
                    image_url = entry.media_thumbnail[0].get("url")
                elif entry.get("media_content"):
                    for media in entry.media_content:
                        if "image" in media.get("type", ""):
                            image_url = media.get("url")
                            break
                elif entry.get("enclosures"):
                    for enc in entry.enclosures:
                        if "image" in enc.get("type", ""):
                            image_url = enc.get("href")
                            break

                # Parse published date
                published = entry.get("published", entry.get("updated", ""))

                all_articles.append({
                    "source": feed_name,
                    "source_id": entry.get("id", link),
                    "title": title,
                    "description": description[:500] if description else "",
                    "content": description,  # RSS typically only provides summary
                    "url": link,
                    "image_url": image_url,
                    "author": entry.get("author", feed_name),
                    "published_at": published,
                })
                count += 1

            print(f"[RSS] Fetched {count} articles from '{feed_name}'")

        except Exception as e:
            print(f"[RSS] Error parsing '{feed_name}': {e}")

    return all_articles
