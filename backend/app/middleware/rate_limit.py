"""Small per-process limiter for authentication and AI-backed attempt creation."""

from collections import defaultdict, deque
from threading import Lock
import time

from fastapi import Request
from fastapi.responses import JSONResponse

_hits: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()
_WINDOW_SECONDS = 60


def _limited_operation(request: Request) -> tuple[str, int] | None:
    if request.method != "POST":
        return None
    path = request.url.path.rstrip("/")
    if path in {"/api/auth/login", "/api/auth/register"}:
        return path, 10
    if path == "/api/assessments" or path.endswith("/retake"):
        return "assessment-generation", 10
    return None


async def sensitive_endpoint_rate_limit(request: Request, call_next):
    operation = _limited_operation(request)
    if operation is None:
        return await call_next(request)

    name, limit = operation
    host = request.client.host if request.client else "unknown"
    key = f"{host}:{name}"
    now = time.monotonic()
    with _lock:
        if len(_hits) > 4096:
            for old_key, old_hits in list(_hits.items()):
                if not old_hits or now - old_hits[-1] >= _WINDOW_SECONDS:
                    _hits.pop(old_key, None)
        hits = _hits[key]
        while hits and now - hits[0] >= _WINDOW_SECONDS:
            hits.popleft()
        if len(hits) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please wait a minute and try again."},
                headers={"Retry-After": str(_WINDOW_SECONDS)},
            )
        hits.append(now)

    return await call_next(request)
