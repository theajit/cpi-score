import json
import logging
import time
import traceback
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, JSONResponse

logger = logging.getLogger("cpi-api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

cpi_store = {
    "data": [],
    "by_iso2": {},
    "by_iso3": {},
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_path = Path(__file__).parent / "data" / "cpi_score.json"
    logger.info(f"Loading CPI data from {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        cpi_store["data"] = json.load(f)
    cpi_store["by_iso2"] = {c["iso2"].upper(): c for c in cpi_store["data"]}
    cpi_store["by_iso3"] = {c["iso3"].upper(): c for c in cpi_store["data"]}
    logger.info(f"Loaded {len(cpi_store['data'])} countries")
    yield


app = FastAPI(
    title="CPI Score API",
    description="Corruption Perceptions Index — Public REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# HTTP middleware to log requests, timing, and basic request metadata
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    client = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    qs = str(request.url.query) if request.url.query else ""

    # Helper to mask sensitive data
    SENSITIVE_KEYS = {"password", "token", "authorization", "access_token", "secret", "api_key", "apikey"}
    MAX_LOG_BYTES = 4096

    def _mask_headers(hdrs: dict):
        out = {}
        for k, v in hdrs.items():
            if k.lower() in ("authorization", "proxy-authorization"):
                out[k] = "[REDACTED]"
            elif any(sk in k.lower() for sk in ("api-key", "apikey", "x-api-key")):
                out[k] = "[REDACTED]"
            else:
                out[k] = v
        return out

    def _mask_json(obj):
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if k.lower() in SENSITIVE_KEYS:
                    out[k] = "[REDACTED]"
                else:
                    out[k] = _mask_json(v)
            return out
        elif isinstance(obj, list):
            return [_mask_json(i) for i in obj]
        else:
            return obj

    body_preview = None
    content_type = request.headers.get("content-type", "")

    # Only attempt to read body for methods that usually have one
    if request.method in ("GET", "POST", "PUT", "PATCH"):
        try:
            body_bytes = await request.body()
            # Recreate receive so downstream can read the body normally
            async def _receive():
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request._receive = _receive

            if body_bytes:
                if "application/json" in content_type:
                    try:
                        parsed = json.loads(body_bytes)
                        masked = _mask_json(parsed)
                        body_preview = json.dumps(masked, ensure_ascii=False)
                    except Exception:
                        body_preview = "<invalid-json>"
                else:
                    # Don't attempt to decode potentially large/binary bodies
                    try:
                        text = body_bytes.decode("utf-8", errors="replace")
                        body_preview = text
                    except Exception:
                        body_preview = f"<{content_type} {len(body_bytes)} bytes>"

                # Truncate previews to a safe size
                if body_preview and len(body_preview) > MAX_LOG_BYTES:
                    body_preview = body_preview[:MAX_LOG_BYTES] + "...[truncated]"
        except Exception:
            logger.exception("Failed to read request body for logging")

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:  # capture unexpected errors
        status_code = 500
        logger.error(
            "Unhandled exception while processing request",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "query": qs,
                "client": client,
                "user_agent": ua,
                "error": repr(exc),
            },
        )
        logger.error(traceback.format_exc())
        raise
    finally:
        duration = (time.time() - start) * 1000.0
        level = logging.INFO if duration < 2000 else logging.WARNING
        hdrs = _mask_headers(dict(request.headers))
        log_extra = {
            "method": request.method,
            "path": str(request.url.path),
            "query": qs,
            "client": client,
            "user_agent": ua,
            "duration_ms": duration,
            "status_code": status_code,
            "headers": hdrs,
        }
        if body_preview is not None:
            log_extra["request_body_preview"] = body_preview

        logger.log(
            level,
            f"{request.method} {request.url.path} {status_code} {duration:.1f}ms",
            extra=log_extra,
        )
    return response


# Generic exception handler that logs request context and stack trace
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    client = request.client.host if request.client else "unknown"
    logger.exception(
        "Exception handled: %s %s from %s\nQuery: %s\nHeaders: %s",
        request.method,
        request.url.path,
        client,
        request.url.query,
        {k: v for k, v in request.headers.items() if k.lower() in ("host", "user-agent", "content-type")},
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

from app.routes import router
app.include_router(router)
