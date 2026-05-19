from pydantic import BaseModel, EmailStr
from typing import Optional


# ─── Response Models ───

class ArticleResponse(BaseModel):
    id: int
    source: str
    title: str
    description: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None


class ClusterResponse(BaseModel):
    id: int
    topic: str
    representative_title: Optional[str] = None
    article_count: int
    dominant_sentiment: str = "neutral"
    created_at: Optional[str] = None
    articles: list[ArticleResponse] = []


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class DigestMetaResponse(BaseModel):
    last_updated: Optional[str] = None
    total_articles: int = 0
    total_clusters: int = 0


class DigestDataResponse(BaseModel):
    clusters: list[ClusterResponse]
    pagination: PaginationResponse


class DigestResponse(BaseModel):
    success: bool = True
    data: DigestDataResponse
    meta: DigestMetaResponse


class TopicResponse(BaseModel):
    topic: str
    article_count: int


class TopicsListResponse(BaseModel):
    success: bool = True
    data: list[TopicResponse]


class StatsResponse(BaseModel):
    success: bool = True
    data: dict


# ─── Request Models ───

class SubscriptionRequest(BaseModel):
    email: str
    topic: str


class SubscriptionResponse(BaseModel):
    id: int
    email: str
    topic: str
    created_at: Optional[str] = None


class ApiKeyRequest(BaseModel):
    owner: str


class ApiKeyResponse(BaseModel):
    key: str
    owner: str
    message: str = "Store this key safely. It cannot be retrieved again."


class AdminConfigRequest(BaseModel):
    cluster_similarity_threshold: Optional[float] = None
    fetch_interval_minutes: Optional[int] = None


class AdminConfigResponse(BaseModel):
    success: bool = True
    config: dict


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


class MessageResponse(BaseModel):
    success: bool = True
    message: str
