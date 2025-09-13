import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import Response

from pipeline.classify import classify_consciousness_level
from pipeline.schema import ConsciousnessLevel

app = FastAPI(title="Bewusstheitsuebung API")
logger = logging.getLogger("uvicorn.error")  # Uvicorn's logger

# =========================
# CORS (env-driven)
# =========================
# Semicolon-separated list (matches your current setup)
allowed_origins = os.getenv("ALLOW_ORIGINS")  # e.g. "https://www.bewusstheitsuebung.de;https://staging.example"
if allowed_origins:
    origin_list = [o.strip() for o in allowed_origins.split(";") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# =========================
# Trusted hosts (optional)
# =========================
# Only allow these Host headers (semicolon-separated). Example: "www.bewusstheitsuebung.de;api.bewusstheitsuebung.de"
allowed_hosts = os.getenv("ALLOW_HOSTS")
if allowed_hosts:
    hosts_list = [h.strip() for h in allowed_hosts.split(";") if h.strip()]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts_list)

# =========================
# Security headers (env-driven)
# =========================
ENABLE_SECURITY_HEADERS = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"

HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
HSTS_INCLUDE_SUBDOMAINS = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
HSTS_PRELOAD = os.getenv("HSTS_PRELOAD", "false").lower() == "true"

CONTENT_SECURITY_POLICY = os.getenv(
    "CONTENT_SECURITY_POLICY",
    # Very strict for APIs (not serving HTML)
    "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none';",
)
REFERRER_POLICY = os.getenv("REFERRER_POLICY", "no-referrer")
PERMISSIONS_POLICY = os.getenv("PERMISSIONS_POLICY", "geolocation=(), microphone=(), camera=(), payment=()")
X_FRAME_OPTIONS = os.getenv("X_FRAME_OPTIONS", "DENY")

# Optional global cache control (off by default)
CACHE_CONTROL = os.getenv("CACHE_CONTROL", "")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    if ENABLE_SECURITY_HEADERS:
        hsts = f"max-age={HSTS_MAX_AGE}"
        if HSTS_INCLUDE_SUBDOMAINS:
            hsts += "; includeSubDomains"
        if HSTS_PRELOAD:
            hsts += "; preload"
        response.headers.setdefault("Strict-Transport-Security", hsts)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", X_FRAME_OPTIONS)
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        response.headers.setdefault("Referrer-Policy", REFERRER_POLICY)
        response.headers.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        if CACHE_CONTROL:
            response.headers.setdefault("Cache-Control", CACHE_CONTROL)
    return response


# =========================
# Request size guard
# =========================
# Reject large bodies early (helps against abuse). Example: MAX_BODY_BYTES="200000" (~200 KB)
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", "0"))  # 0 disables the check


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if MAX_BODY_BYTES > 0:
        cl = request.headers.get("content-length")
        try:
            if cl is not None and int(cl) > MAX_BODY_BYTES:
                return Response(
                    content='{"detail":"Request entity too large"}',
                    status_code=413,
                    media_type="application/json",
                )
        except ValueError:
            # If header malformed, proceed to avoid false positives
            pass
    return await call_next(request)


# =========================
# Models & routes
# =========================
class ClassifyRequest(BaseModel):
    messages: List[str] = Field(..., description="Conversation history; last item is target.")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/healthz-headers")
def healthz_headers():
    """Return the configured header values for verification."""
    hsts = f"max-age={HSTS_MAX_AGE}"
    if HSTS_INCLUDE_SUBDOMAINS:
        hsts += "; includeSubDomains"
    if HSTS_PRELOAD:
        hsts += "; preload"
    return {
        "security_headers_enabled": ENABLE_SECURITY_HEADERS,
        "Strict-Transport-Security": hsts if ENABLE_SECURITY_HEADERS else None,
        "X-Content-Type-Options": "nosniff" if ENABLE_SECURITY_HEADERS else None,
        "X-Frame-Options": X_FRAME_OPTIONS if ENABLE_SECURITY_HEADERS else None,
        "X-XSS-Protection": "1; mode=block" if ENABLE_SECURITY_HEADERS else None,
        "Referrer-Policy": REFERRER_POLICY if ENABLE_SECURITY_HEADERS else None,
        "Permissions-Policy": PERMISSIONS_POLICY if ENABLE_SECURITY_HEADERS else None,
        "Content-Security-Policy": CONTENT_SECURITY_POLICY if ENABLE_SECURITY_HEADERS else None,
        "CORS_ALLOW_ORIGINS": [o.strip() for o in (allowed_origins or "").split(";") if o.strip()],
        "TRUSTED_HOSTS": [h.strip() for h in (allowed_hosts or "").split(";") if h.strip()],
        "MAX_BODY_BYTES": MAX_BODY_BYTES,
        "Cache-Control": CACHE_CONTROL or None,
    }


@app.post("/classify", response_model=ConsciousnessLevel, status_code=status.HTTP_200_OK)
def classify(req: ClassifyRequest):
    try:
        return classify_consciousness_level(req.messages)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in /classify: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
