from fastapi import APIRouter, Request
from server.database import get_clusters_by_topic, get_all_topics
from server.middleware.cache import cache
from server.middleware.rate_limiter import limiter

router = APIRouter(prefix="/api", tags=["Topics"])


@router.get("/topics", summary="List all available topics")
@limiter.limit("100/15minutes")
async def list_topics(request: Request):
    """Get all topics with their article counts."""
    cache_key = "topics:all"
    cached = cache.get(cache_key)
    if cached:
        return cached

    topics = await get_all_topics()
    response = {"success": True, "data": topics}

    cache.set(cache_key, response)
    return response


@router.get("/topic/{name}", summary="Get clusters filtered by topic")
@limiter.limit("100/15minutes")
async def get_topic(request: Request, name: str):
    """
    Get clusters matching a topic name.
    Uses fuzzy matching (SQL LIKE) so partial names work.
    """
    cache_key = f"topic:{name.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    clusters = await get_clusters_by_topic(name)
    response = {
        "success": True,
        "data": {"clusters": clusters, "topic": name},
    }

    cache.set(cache_key, response)
    return response
