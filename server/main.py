from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os

from server.config import settings
from server.database import init_db, shutdown_db
from server.scheduler import start_scheduler, stop_scheduler
from server.middleware.rate_limiter import limiter
from server.routes import digest, topics, subscriptions, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    # Startup
    await init_db()
    start_scheduler()
    print(f"[App] Server starting on port {settings.port}")
    print(f"[App] Swagger docs at http://localhost:{settings.port}/docs")
    print(f"[App] ReDoc at http://localhost:{settings.port}/redoc")

    yield

    # Shutdown
    stop_scheduler()
    await shutdown_db()
    print("[App] Server shut down")


# ─── FastAPI App ───

app = FastAPI(
    title="Multi-Source News Digest API",
    description=(
        "A multi-source news aggregation service that collects articles from NewsAPI, "
        "The Guardian, and RSS feeds, generates AI summaries using Gemini, clusters "
        "related stories, and serves everything through a REST API."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middleware ───

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Routes ───

app.include_router(digest.router)
app.include_router(topics.router)
app.include_router(subscriptions.router)
app.include_router(admin.router)


# ─── Health Check ───

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "news-digest-api"}


# ─── Serve React Frontend (production) ───

# Check if React build exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "client", "dist")
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(request: Request, full_path: str):
        """Serve React app for non-API routes."""
        # Don't serve frontend for API routes
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)

        # Try to serve the requested file
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fall back to index.html for SPA routing
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return JSONResponse({"error": "Not found"}, status_code=404)


# ─── Run ───

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=settings.port, reload=settings.is_dev)
