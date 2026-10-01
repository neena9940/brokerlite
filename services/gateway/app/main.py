import redis
import httpx
from fastapi import FastAPI, Request, HTTPException, Response
from jose import jwt, JWTError
from app.config import settings, ROUTES, PUBLIC_PATHS

app = FastAPI(title="BrokerLite API Gateway")

# Redis client for rate limiting
r = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def authenticate(request: Request) -> str:
    """Validates the JWT. Returns user_id, or raises 401."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = auth_header.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Wrong token type")
        return payload["sub"]  # Returns the user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def rate_limit(user_id: str) -> None:
    """Fixed window rate limiter: 100 requests per 60 seconds per user."""
    key = f"rate:{user_id}"
    # INCR is atomic. If it's the first request, set the 60s expiration.
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    if count > 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


@app.api_route("/{segment}/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(segment: str, full_path: str, request: Request):
    # 1. Look up where to send this request
    target_base = ROUTES.get(segment)
    if target_base is None:
        raise HTTPException(status_code=404, detail="Unknown route")

    # 2. Reconstruct the path (e.g., segment="market", full_path="prices/AAPL")
    full_url_path = f"/{full_path}".rstrip("/")

    # 3. Security checks (skip for public paths like /auth/login)
    user_id = None
    if full_url_path not in PUBLIC_PATHS:
        user_id = authenticate(request)  # Fails fast with 401 if invalid
        rate_limit(user_id)  # Fails fast with 429 if over limit

    # 4. Forward the request to the backend service
    body = await request.body()  # Capture the raw JSON body

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Forward the request, stripping the "segment" from the URL
        # e.g., Gateway receives /market/prices/AAPL -> forwards to http://localhost:8001/prices/AAPL
        upstream_response = await client.request(
            method=request.method,
            url=f"{target_base}{full_url_path}",
            params=dict(request.query_params),
            content=body,
            headers={
                "Content-Type": "application/json",
                # Optional: Forward the user_id to the backend so it knows who is acting
                "X-User-Id": user_id if user_id else "anonymous"
            }
        )

    # 5. Return the backend's response exactly as it was, to the frontend
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        media_type=upstream_response.headers.get("content-type", "application/json")
    )