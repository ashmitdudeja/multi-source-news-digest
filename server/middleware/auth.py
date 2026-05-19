from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from server.database import get_api_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    """
    API key authentication dependency.
    Bypass for:
    - Static files
    - Swagger docs (/docs, /redoc, /openapi.json)
    - Auth registration endpoint
    """
    path = request.url.path

    # Bypass paths that don't need auth
    bypass_paths = ["/docs", "/redoc", "/openapi.json", "/api/auth/register", "/"]
    if any(path.startswith(bp) for bp in bypass_paths):
        return None

    # Also bypass static file requests
    if path.startswith("/assets") or path.endswith((".js", ".css", ".html", ".ico", ".png", ".svg")):
        return None

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Include X-API-Key header.")

    key_data = await get_api_key(api_key)
    if not key_data:
        raise HTTPException(status_code=403, detail="Invalid or inactive API key.")

    return key_data
