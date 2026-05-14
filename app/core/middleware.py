import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


def setup_middleware(app: FastAPI, settings):

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"]
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        response = await call_next(request)
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[{request_id}] {response.status_code} — {duration}ms")
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration}ms"
        return response