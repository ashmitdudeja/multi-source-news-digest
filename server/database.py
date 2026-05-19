import sqlalchemy
from databases import Database
from datetime import datetime, timezone
import os

# ─── Database Setup ───

DATABASE_URL = "sqlite+aiosqlite:///./data/news_digest.db"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

metadata = sqlalchemy.MetaData()

# ─── Table Definitions ───

articles = sqlalchemy.Table(
    "articles",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("source", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("source_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("description", sqlalchemy.Text, nullable=True),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=True),
    sqlalchemy.Column("url", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("image_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("author", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("published_at", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("fetched_at", sqlalchemy.String, nullable=False),
)

summaries = sqlalchemy.Table(
    "summaries",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("article_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True),
    sqlalchemy.Column("summary_text", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("sentiment", sqlalchemy.String, nullable=False, default="neutral"),
    sqlalchemy.Column("generated_at", sqlalchemy.String, nullable=False),
)

clusters = sqlalchemy.Table(
    "clusters",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("topic", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("representative_title", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("updated_at", sqlalchemy.String, nullable=False),
)

cluster_articles = sqlalchemy.Table(
    "cluster_articles",
    metadata,
    sqlalchemy.Column("cluster_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False),
    sqlalchemy.Column("article_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
    sqlalchemy.PrimaryKeyConstraint("cluster_id", "article_id"),
)

subscriptions = sqlalchemy.Table(
    "subscriptions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("topic", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String, nullable=False),
    sqlalchemy.UniqueConstraint("email", "topic"),
)

api_keys = sqlalchemy.Table(
    "api_keys",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("key_value", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("owner", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("is_active", sqlalchemy.Integer, nullable=False, default=1),
)

# ─── Database Instance ───

database = Database(DATABASE_URL)


async def init_db():
    """Create tables if they don't exist."""
    engine = sqlalchemy.create_engine(DATABASE_URL.replace("+aiosqlite", ""))
    metadata.create_all(engine)
    engine.dispose()
    await database.connect()
    print("[DB] Database initialized and connected")


async def shutdown_db():
    """Close database connection."""
    await database.disconnect()
    print("[DB] Database disconnected")


# ─── URL Normalization ───

def normalize_url(url: str) -> str:
    """Normalize URL for deduplication: strip trailing slashes, fragments, lowercase."""
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # Keep scheme, host, path — strip fragment and common tracking params
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",  # params
            "",  # query (strip tracking params)
            "",  # fragment
        ))
        return normalized
    except Exception:
        return url.lower().rstrip("/")


# ─── Article Operations ───

async def insert_article(article: dict) -> int | None:
    """Insert article if URL doesn't already exist. Returns ID or None if duplicate."""
    normalized = normalize_url(article["url"])

    # Check for existing
    query = articles.select().where(articles.c.url == normalized)
    existing = await database.fetch_one(query)
    if existing:
        return None

    now = datetime.now(timezone.utc).isoformat()
    query = articles.insert().values(
        source=article["source"],
        source_id=article.get("source_id"),
        title=article["title"],
        description=article.get("description", ""),
        content=article.get("content", ""),
        url=normalized,
        image_url=article.get("image_url"),
        author=article.get("author"),
        published_at=article.get("published_at", now),
        fetched_at=now,
    )
    last_id = await database.execute(query)
    return last_id


async def insert_articles_batch(article_list: list[dict]) -> int:
    """Insert multiple articles, skipping duplicates. Returns count inserted."""
    inserted = 0
    for article in article_list:
        result = await insert_article(article)
        if result is not None:
            inserted += 1
    return inserted


async def get_unsummarized_articles() -> list[dict]:
    """Get articles that don't have summaries yet."""
    query = """
        SELECT a.* FROM articles a
        LEFT JOIN summaries s ON a.id = s.article_id
        WHERE s.id IS NULL
        ORDER BY a.fetched_at DESC
    """
    rows = await database.fetch_all(query=query)
    return [dict(r._mapping) for r in rows]


async def get_recent_articles(hours: int = 24) -> list[dict]:
    """Get recent articles with summaries."""
    query = """
        SELECT a.*, s.summary_text, s.sentiment
        FROM articles a
        LEFT JOIN summaries s ON a.id = s.article_id
        WHERE a.fetched_at >= datetime('now', :offset)
        ORDER BY a.published_at DESC
    """
    rows = await database.fetch_all(query=query, values={"offset": f"-{hours} hours"})
    return [dict(r._mapping) for r in rows]


async def insert_summary(article_id: int, summary_text: str, sentiment: str):
    """Insert or update summary for an article."""
    now = datetime.now(timezone.utc).isoformat()
    # Try update first
    query = summaries.select().where(summaries.c.article_id == article_id)
    existing = await database.fetch_one(query)
    if existing:
        update_query = (
            summaries.update()
            .where(summaries.c.article_id == article_id)
            .values(summary_text=summary_text, sentiment=sentiment, generated_at=now)
        )
        await database.execute(update_query)
    else:
        insert_query = summaries.insert().values(
            article_id=article_id,
            summary_text=summary_text,
            sentiment=sentiment,
            generated_at=now,
        )
        await database.execute(insert_query)


# ─── Cluster Operations ───

async def reset_clusters(cluster_data: list[dict]):
    """Clear existing clusters and insert new ones."""
    now = datetime.now(timezone.utc).isoformat()

    await database.execute(query="DELETE FROM cluster_articles")
    await database.execute(query="DELETE FROM clusters")

    for cluster in cluster_data:
        cluster_id = await database.execute(
            clusters.insert().values(
                topic=cluster["topic"],
                representative_title=cluster.get("representative_title", ""),
                created_at=now,
                updated_at=now,
            )
        )
        for article_id in cluster["article_ids"]:
            await database.execute(
                cluster_articles.insert().values(
                    cluster_id=cluster_id,
                    article_id=article_id,
                )
            )


async def get_clusters_with_articles() -> list[dict]:
    """Get all clusters with their articles and summaries."""
    query = """
        SELECT 
            c.id as cluster_id,
            c.topic,
            c.representative_title,
            c.created_at as cluster_created_at,
            a.id as article_id,
            a.source,
            a.title,
            a.description,
            a.url,
            a.image_url,
            a.author,
            a.published_at,
            s.summary_text,
            s.sentiment
        FROM clusters c
        JOIN cluster_articles ca ON c.id = ca.cluster_id
        JOIN articles a ON ca.article_id = a.id
        LEFT JOIN summaries s ON a.id = s.article_id
        ORDER BY c.id, a.published_at DESC
    """
    rows = await database.fetch_all(query=query)
    return _group_clusters([dict(r._mapping) for r in rows])


async def get_clusters_by_topic(topic: str) -> list[dict]:
    """Get clusters matching a topic name (fuzzy via LIKE)."""
    query = """
        SELECT 
            c.id as cluster_id,
            c.topic,
            c.representative_title,
            c.created_at as cluster_created_at,
            a.id as article_id,
            a.source,
            a.title,
            a.description,
            a.url,
            a.image_url,
            a.author,
            a.published_at,
            s.summary_text,
            s.sentiment
        FROM clusters c
        JOIN cluster_articles ca ON c.id = ca.cluster_id
        JOIN articles a ON ca.article_id = a.id
        LEFT JOIN summaries s ON a.id = s.article_id
        WHERE LOWER(c.topic) LIKE LOWER(:topic)
        ORDER BY c.id, a.published_at DESC
    """
    rows = await database.fetch_all(query=query, values={"topic": f"%{topic}%"})
    return _group_clusters([dict(r._mapping) for r in rows])


def _group_clusters(rows: list[dict]) -> list[dict]:
    """Group flat joined rows into nested cluster → articles structure."""
    clusters_map = {}
    for row in rows:
        cid = row["cluster_id"]
        if cid not in clusters_map:
            clusters_map[cid] = {
                "id": cid,
                "topic": row["topic"],
                "representative_title": row["representative_title"],
                "created_at": row["cluster_created_at"],
                "articles": [],
            }
        clusters_map[cid]["articles"].append({
            "id": row["article_id"],
            "source": row["source"],
            "title": row["title"],
            "description": row["description"],
            "url": row["url"],
            "image_url": row["image_url"],
            "author": row["author"],
            "published_at": row["published_at"],
            "summary": row["summary_text"],
            "sentiment": row["sentiment"],
        })

    result = list(clusters_map.values())
    for cluster in result:
        cluster["article_count"] = len(cluster["articles"])
        # Determine dominant sentiment
        sentiments = [a["sentiment"] for a in cluster["articles"] if a["sentiment"]]
        if sentiments:
            from collections import Counter
            cluster["dominant_sentiment"] = Counter(sentiments).most_common(1)[0][0]
        else:
            cluster["dominant_sentiment"] = "neutral"

    return result


async def get_all_topics() -> list[dict]:
    """Get all topics with article counts."""
    query = """
        SELECT c.topic, COUNT(ca.article_id) as article_count
        FROM clusters c
        JOIN cluster_articles ca ON c.id = ca.cluster_id
        GROUP BY c.topic
        ORDER BY article_count DESC
    """
    rows = await database.fetch_all(query=query)
    return [dict(r._mapping) for r in rows]


async def get_stats() -> dict:
    """Get database statistics."""
    total_articles = await database.fetch_one("SELECT COUNT(*) as count FROM articles")
    total_clusters = await database.fetch_one("SELECT COUNT(*) as count FROM clusters")
    total_summaries = await database.fetch_one("SELECT COUNT(*) as count FROM summaries")

    source_query = "SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC"
    source_rows = await database.fetch_all(source_query)

    return {
        "total_articles": total_articles["count"] if total_articles else 0,
        "total_clusters": total_clusters["count"] if total_clusters else 0,
        "total_summaries": total_summaries["count"] if total_summaries else 0,
        "sources": [dict(r._mapping) for r in source_rows],
    }


async def delete_old_articles(days: int):
    """Delete articles older than specified days."""
    query = f"DELETE FROM articles WHERE fetched_at < datetime('now', '-{days} days')"
    await database.execute(query=query)


# ─── Subscription Operations ───

async def insert_subscription(email: str, topic: str) -> int:
    """Create a topic subscription."""
    now = datetime.now(timezone.utc).isoformat()
    sub_id = await database.execute(
        subscriptions.insert().values(email=email, topic=topic, created_at=now)
    )
    return sub_id


async def get_subscriptions_by_email(email: str) -> list[dict]:
    query = subscriptions.select().where(subscriptions.c.email == email)
    rows = await database.fetch_all(query)
    return [dict(r._mapping) for r in rows]


async def delete_subscription(sub_id: int):
    query = subscriptions.delete().where(subscriptions.c.id == sub_id)
    await database.execute(query)


# ─── API Key Operations ───

async def insert_api_key(key_value: str, owner: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    key_id = await database.execute(
        api_keys.insert().values(key_value=key_value, owner=owner, created_at=now, is_active=1)
    )
    return key_id


async def get_api_key(key_value: str) -> dict | None:
    query = api_keys.select().where(
        (api_keys.c.key_value == key_value) & (api_keys.c.is_active == 1)
    )
    row = await database.fetch_one(query)
    return dict(row._mapping) if row else None
