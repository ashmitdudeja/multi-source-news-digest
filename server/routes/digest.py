from fastapi import APIRouter, Query, Request
from server.database import get_clusters_with_articles, get_stats
from server.middleware.cache import cache
from server.middleware.rate_limiter import limiter
from server.models import DigestResponse, StatsResponse
from datetime import datetime, timezone
import math

router = APIRouter(prefix="/api/digest", tags=["Digest"])


@router.get("", response_model=DigestResponse, summary="Get all clustered news")
@limiter.limit("100/15minutes")
async def get_digest(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
):
    """
    Get all clustered news articles with summaries and sentiment.
    Results are paginated and cached for 5 minutes.
    """
    cache_key = f"digest:page={page}&limit={limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    clusters = await get_clusters_with_articles()
    total = len(clusters)
    total_pages = math.ceil(total / limit) if total > 0 else 1

    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated_clusters = clusters[start:end]

    stats = await get_stats()

    response = {
        "success": True,
        "data": {
            "clusters": paginated_clusters,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
            },
        },
        "meta": {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_articles": stats["total_articles"],
            "total_clusters": stats["total_clusters"],
        },
    }

    cache.set(cache_key, response)
    return response


@router.get("/latest", summary="Get the most recent digest")
@limiter.limit("100/15minutes")
async def get_latest_digest(request: Request):
    """Get the latest clusters (page 1, limit 5)."""
    cache_key = "digest:latest"
    cached = cache.get(cache_key)
    if cached:
        return cached

    clusters = await get_clusters_with_articles()
    latest = clusters[:5]

    response = {
        "success": True,
        "data": {"clusters": latest},
        "meta": {"last_updated": datetime.now(timezone.utc).isoformat()},
    }

    cache.set(cache_key, response)
    return response


@router.get("/stats", response_model=StatsResponse, summary="Get digest statistics")
@limiter.limit("100/15minutes")
async def get_digest_stats(request: Request):
    """Get statistics: total articles, clusters, source breakdown."""
    cache_key = "digest:stats"
    cached = cache.get(cache_key)
    if cached:
        return cached

    stats = await get_stats()
    response = {"success": True, "data": stats}

    cache.set(cache_key, response)
    return response
