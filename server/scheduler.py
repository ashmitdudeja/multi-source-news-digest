import asyncio
from datetime import timedelta
from server.config import settings
from server.services.collector import collect_all_articles
from server.services.summarizer import summarize_articles
from server.services.clusterer import cluster_articles
from server.database import delete_old_articles
from server.middleware.cache import cache


# Module-level state for the background task
_scheduler_task = None
_running = False


async def fetch_and_process():
    """Main scheduled job: fetch → summarize → cluster → clear cache."""
    print("[Scheduler] Starting scheduled fetch & process cycle...")
    try:
        await collect_all_articles()
        await summarize_articles()
        await cluster_articles()
        cache.clear()
        print("[Scheduler] Cycle completed successfully")
    except Exception as e:
        print(f"[Scheduler] Error in cycle: {e}")


async def cleanup_old_articles_job():
    """Daily cleanup of old articles."""
    print("[Scheduler] Cleaning up old articles...")
    try:
        await delete_old_articles(settings.article_retention_days)
        print(f"[Scheduler] Cleaned articles older than {settings.article_retention_days} days")
    except Exception as e:
        print(f"[Scheduler] Error in cleanup: {e}")


async def _scheduler_loop():
    """Background loop that runs fetch_and_process at configured intervals."""
    global _running
    fetch_interval = settings.fetch_interval_minutes * 60  # Convert to seconds
    cleanup_counter = 0

    while _running:
        try:
            await fetch_and_process()
        except Exception as e:
            print(f"[Scheduler] Unexpected error: {e}")

        cleanup_counter += 1
        # Run cleanup roughly every 48 cycles (~24 hours at 30-min intervals)
        if cleanup_counter >= 48:
            await cleanup_old_articles_job()
            cleanup_counter = 0

        # Sleep for the configured interval
        try:
            await asyncio.sleep(fetch_interval)
        except asyncio.CancelledError:
            break


def start_scheduler():
    """Start the background scheduler loop."""
    global _scheduler_task, _running
    _running = True

    loop = asyncio.get_event_loop()
    _scheduler_task = loop.create_task(_scheduler_loop())

    print(f"[Scheduler] Started — fetching every {settings.fetch_interval_minutes} minutes")


def stop_scheduler():
    """Gracefully stop the scheduler."""
    global _scheduler_task, _running
    _running = False

    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        print("[Scheduler] Stopped")
