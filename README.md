# Multi-Source News Digest API

A production-grade news aggregation service that collects articles from multiple sources, generates AI summaries using Google Gemini, clusters related stories using TF-IDF + cosine similarity, and serves everything through a REST API with a modern React frontend.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-06B6D4?logo=tailwindcss)

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        APScheduler (30 min)                     │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│         ┌─────────┐   ┌───────────┐   ┌───────────┐           │
│         │ NewsAPI  │   │ Guardian  │   │ RSS Feeds │           │
│         │   .org   │   │   API     │   │ BBC/Reuters│          │
│         └────┬─────┘   └─────┬─────┘   └─────┬─────┘          │
│              └───────────────┼───────────────┘                  │
│                              ▼                                  │
│                    ┌──────────────────┐                         │
│                    │  Normalize &     │                         │
│                    │  Dedup (URL)     │                         │
│                    └────────┬─────────┘                         │
│                             ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  SQLite Database │                         │
│                    └────────┬─────────┘                         │
│                             │                                   │
│              ┌──────────────┴──────────────┐                   │
│              ▼                             ▼                    │
│    ┌──────────────────┐          ┌──────────────────┐          │
│    │  Gemini 2.5 Flash │          │ sklearn TF-IDF + │          │
│    │  Summarizer +     │          │ Cosine Similarity │         │
│    │  Sentiment        │          │ Clusterer         │         │
│    └──────────────────┘          └──────────────────┘          │
│                                                                 │
│    ┌──────────────────────────────────────────────────────┐    │
│    │                  FastAPI Server                       │    │
│    │  /api/digest  /api/topics  /api/topic/{name}         │    │
│    │  /docs (Swagger)  /redoc                             │    │
│    └───────────────────────┬──────────────────────────────┘    │
│                            ▼                                    │
│    ┌──────────────────────────────────────────────────────┐    │
│    │           React + Tailwind CSS Frontend              │    │
│    └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## Features

### Core
- **3 News Sources**: NewsAPI.org, The Guardian, BBC/Reuters RSS feeds
- **AI Summarization**: 2-line summaries via Google Gemini 2.5 Flash with smart extractive fallback
- **Article Clustering**: TF-IDF vectorization + cosine similarity (scikit-learn)
- **REST API**: Full CRUD with pagination, filtering, structured JSON responses
- **Scheduled Fetching**: APScheduler runs every 30 minutes

### Bonus
- ✅ **Sentiment Tagging**: Positive / Neutral / Negative per article
- ✅ **Topic Subscriptions**: Email-based topic alerts
- ✅ **API Key Authentication**: `X-API-Key` header auth
- ✅ **Rate Limiting**: 100 req/15min per IP via slowapi
- ✅ **API Documentation**: Auto-generated Swagger + ReDoc (FastAPI built-in)
- ✅ **In-Memory Caching**: TTL cache with scheduler-triggered invalidation

## Tech Stack

| Layer | Technology |
|:---|:---|
| Backend | Python 3.11+, FastAPI, SQLite, SQLAlchemy |
| AI/ML | Google Gemini 2.5 Flash, scikit-learn |
| Frontend | React 19 (Vite), Tailwind CSS 3.4 |
| Scheduling | APScheduler |
| Rate Limiting | slowapi |

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- API Keys (all free):
  - [NewsAPI.org](https://newsapi.org/register)
  - [The Guardian](https://open-platform.theguardian.com/access/)
  - [Google AI Studio](https://aistudio.google.com/) (Gemini)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd multi-source-news-digest

# Create .env from template
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m server.main
```

Server runs at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd client
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (proxies API calls to backend)

### 4. Trigger Initial Data Fetch

```bash
curl -X POST http://localhost:8000/api/admin/refresh
```

## API Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/digest?page=1&limit=10` | Paginated clustered news |
| `GET` | `/api/digest/latest` | Most recent 5 clusters |
| `GET` | `/api/digest/stats` | Total articles, clusters, sources |
| `GET` | `/api/topics` | List all topics with counts |
| `GET` | `/api/topic/{name}` | Clusters filtered by topic |
| `POST` | `/api/subscriptions` | Subscribe to a topic |
| `GET` | `/api/subscriptions/{email}` | Get subscriptions |
| `DELETE` | `/api/subscriptions/{id}` | Unsubscribe |
| `POST` | `/api/admin/refresh` | Manual fetch + process |
| `GET/POST` | `/api/admin/config` | View/update runtime config |
| `POST` | `/api/auth/register` | Generate API key |
| `GET` | `/api/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

### Example Response — `GET /api/digest`

```json
{
  "success": true,
  "data": {
    "clusters": [
      {
        "id": 1,
        "topic": "AI Regulation",
        "article_count": 3,
        "dominant_sentiment": "neutral",
        "representative_title": "EU passes comprehensive AI safety bill",
        "articles": [
          {
            "id": 1,
            "title": "EU passes comprehensive AI safety bill",
            "source": "The Guardian",
            "summary": "The EU has passed a landmark AI regulation bill...",
            "sentiment": "neutral",
            "url": "https://...",
            "image_url": "https://...",
            "published_at": "2026-05-17T10:00:00Z"
          }
        ]
      }
    ],
    "pagination": { "page": 1, "limit": 10, "total": 15, "total_pages": 2 }
  },
  "meta": {
    "last_updated": "2026-05-17T10:30:00Z",
    "total_articles": 75,
    "total_clusters": 15
  }
}
```

## Design Decisions

1. **Exact URL Dedup Only**: Fuzzy title matching skipped at ingestion — clustering handles same-story grouping with full TF-IDF context
2. **Cluster Threshold 0.45**: Prevents overly broad clusters during breaking news. Runtime-tunable via admin endpoint
3. **Smart Extractive Fallback**: When Gemini is rate-limited, uses sentences 2–4 (skips teaser/hook openers common in Guardian articles)
4. **In-Memory Cache**: Simple `dict` with TTL, invalidated after each scheduler run. No Redis needed at this scale
5. **scikit-learn for Clustering**: `TfidfVectorizer` + `cosine_similarity` in 2 lines vs manual implementation

## License

MIT
