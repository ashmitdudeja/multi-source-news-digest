from fastapi import APIRouter, Request
from server.config import settings
from server.middleware.cache import cache
from server.middleware.rate_limiter import limiter
from server.services.collector import collect_all_articles
from server.services.summarizer import summarize_articles
from server.services.clusterer import cluster_articles
from server.database import insert_api_key
from server.models import AdminConfigRequest, ApiKeyRequest
import uuid

router = APIRouter(prefix="/api", tags=["Admin"])


@router.post("/admin/refresh", summary="Trigger manual fetch + process cycle")
@limiter.limit("5/15minutes")
async def trigger_refresh(request: Request):
    """Manually trigger article collection, summarization, and clustering."""
    print("[Admin] Manual refresh triggered")

    # Collect
    collection_stats = await collect_all_articles()

    # Summarize
    summarized = await summarize_articles()

    # Cluster
    clustered = await cluster_articles()

    # Clear cache after processing
    cache.clear()

    return {
        "success": True,
        "message": "Refresh completed",
        "data": {
            "collection": collection_stats,
            "articles_summarized": summarized,
            "clusters_created": clustered,
        },
    }


@router.get("/admin/config", summary="Get current runtime config")
@limiter.limit("100/15minutes")
async def get_config(request: Request):
    """Get current runtime configuration values."""
    return {
        "success": True,
        "config": {
            "cluster_similarity_threshold": settings.cluster_similarity_threshold,
            "fetch_interval_minutes": settings.fetch_interval_minutes,
            "cache_ttl_seconds": settings.cache_ttl_seconds,
            "article_retention_days": settings.article_retention_days,
        },
    }


@router.post("/admin/config", summary="Update runtime config")
@limiter.limit("5/15minutes")
async def update_config(request: Request, body: AdminConfigRequest):
    """
    Update runtime config (e.g., cluster threshold).
    Changes take effect on next scheduler run.
    """
    updated = {}
    if body.cluster_similarity_threshold is not None:
        settings.cluster_similarity_threshold = body.cluster_similarity_threshold
        updated["cluster_similarity_threshold"] = body.cluster_similarity_threshold

    if body.fetch_interval_minutes is not None:
        settings.fetch_interval_minutes = body.fetch_interval_minutes
        updated["fetch_interval_minutes"] = body.fetch_interval_minutes

    return {
        "success": True,
        "message": "Config updated",
        "updated": updated,
    }


@router.post("/auth/register", summary="Generate a new API key")
@limiter.limit("3/15minutes")
async def register_api_key(request: Request, body: ApiKeyRequest):
    """Generate a new API key for authentication."""
    key = str(uuid.uuid4())
    await insert_api_key(key, body.owner)

    return {
        "success": True,
        "data": {
            "key": key,
            "owner": body.owner,
            "message": "Store this key safely. It cannot be retrieved again.",
        },
    }
