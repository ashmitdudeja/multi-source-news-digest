from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    port: int = 8000
    environment: str = "development"

    # API Keys
    newsapi_key: str = ""
    guardian_api_key: str = ""
    gemini_api_key: str = ""

    # Scheduler
    fetch_interval_minutes: int = 30

    # Clustering
    cluster_similarity_threshold: float = 0.45

    # Rate Limiting
    rate_limit_window_seconds: int = 900  # 15 minutes
    rate_limit_max: int = 100
    rate_limit_write_max: int = 10

    # Cache
    cache_ttl_seconds: int = 300  # 5 minutes

    # Data retention
    article_retention_days: int = 7

    # RSS Feed URLs
    rss_feeds: list[dict] = [
        {"name": "BBC News", "url": "https://feeds.bbci.co.uk/news/rss.xml"},
        {"name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best"},
    ]

    # NewsAPI categories
    newsapi_categories: list[str] = ["technology", "business", "science", "health"]

    # Gemini model
    gemini_model: str = "gemini-2.5-flash"

    # Summarizer batch settings
    summarizer_batch_size: int = 5
    summarizer_batch_delay_seconds: float = 2.0

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"

    @property
    def database_url(self) -> str:
        return "sqlite+aiosqlite:///./data/news_digest.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
