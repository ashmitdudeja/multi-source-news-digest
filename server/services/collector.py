import asyncio
from server.services.newsapi_service import fetch_from_newsapi
from server.services.guardian_service import fetch_from_guardian
from server.services.rss_service import fetch_from_rss
from server.database import insert_articles_batch


async def collect_all_articles() -> dict:
    """
    Orchestrate fetching from all 3 sources concurrently.
    Uses asyncio.gather with return_exceptions=True so one failure
    doesn't block others.
    
    Deduplication: exact URL match only (handled by database layer).
    Fuzzy title matching deliberately skipped — clustering handles
    same-story grouping with full TF-IDF context.

    Returns stats dict with per-source counts.
    """
    print("[Collector] Starting article collection from all sources...")

    results = await asyncio.gather(
        fetch_from_newsapi(),
        fetch_from_guardian(),
        fetch_from_rss(),
        return_exceptions=True,
    )

    source_names = ["NewsAPI", "The Guardian", "RSS Feeds"]
    stats = {"total_fetched": 0, "total_inserted": 0, "sources": {}}
    all_articles = []

    for i, result in enumerate(results):
        source = source_names[i]
        if isinstance(result, Exception):
            print(f"[Collector] {source} failed: {result}")
            stats["sources"][source] = {"fetched": 0, "error": str(result)}
        else:
            count = len(result)
            stats["sources"][source] = {"fetched": count}
            stats["total_fetched"] += count
            all_articles.extend(result)
            print(f"[Collector] {source}: {count} articles fetched")

    # Batch insert with dedup (exact URL match in database layer)
    if all_articles:
        inserted = await insert_articles_batch(all_articles)
        stats["total_inserted"] = inserted
        print(f"[Collector] Inserted {inserted}/{len(all_articles)} articles (rest were duplicates)")
    else:
        print("[Collector] No articles fetched from any source")

    return stats
