import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from psycopg import Error as DatabaseError
from psycopg_pool import PoolTimeout
from starlette.exceptions import HTTPException

from .api.errors import error_response
from .api.routes.operations import router
from .config import settings
from .security import ServiceError
from .services.runtime import Services

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
# Dependency loggers can include URLs or database connection details; avoid emitting them.
for name in ("httpx", "httpcore", "psycopg.pool", "mcp"):
    logging.getLogger(name).setLevel(logging.CRITICAL)
logger = logging.getLogger("schemeradar")
config = settings()
services = Services.create(config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app.state.services.db.open()
    try:
        yield
    finally:
        await app.state.services.db.close()


app = FastAPI(title="SchemeRadar", version="0.1.0", lifespan=lifespan)
app.state.services = services
app.include_router(router, prefix="/api")
app.include_router(router, prefix="/api/v1")
app.add_middleware(CORSMiddleware, allow_origins=[config.frontend_origin], allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"], expose_headers=["X-Request-ID"], allow_credentials=False)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id, start = uuid.uuid4().hex, time.monotonic()
    request.state.request_id = request_id

    def finish(response):
        response.headers["X-Request-ID"] = request_id
        logger.info("request=%s method=%s status=%s duration_ms=%d", request_id, request.method,
                    response.status_code, (time.monotonic() - start) * 1000)
        return response

    # Bound bodies even for chunked requests, before JSON parsing.
    if request.method == "POST":
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 262144:
                return finish(error_response(request, 413, "Request body exceeds 256 KiB."))
        request._body = bytes(body)
    expensive = request.method == "POST" and request.url.path.removeprefix("/api/v1").removeprefix("/api") in {
        "/agent", "/discover", "/discover-and-match", "/research", "/chat", "/search", "/fetch", "/extract"
    }
    if expensive:
        try:
            await asyncio.wait_for(request.app.state.services.slots.acquire(), timeout=0.1)
        except TimeoutError:
            return finish(error_response(request, 429, "Research capacity is busy. Retry shortly."))
    try:
        response = await call_next(request)
    finally:
        if expensive:
            request.app.state.services.slots.release()
    return finish(response)


@app.exception_handler(ServiceError)
async def service_error(request, exc):
    return error_response(request, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Pydantic's default error includes rejected input; do not echo student data or content.
    errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return error_response(request, 422, errors)


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logger.error("Unhandled application failure type=%s", type(exc).__name__)
    return error_response(request, 500, "Unexpected server error. Check backend service health.")


@app.exception_handler(DatabaseError)
@app.exception_handler(PoolTimeout)
async def database_error(request, exc):
    return error_response(request, 503, "PostgreSQL is unavailable or migrations have not been applied.")


@app.exception_handler(TimeoutError)
async def timeout_error(request, exc):
    return error_response(request, 504, "External service exceeded the request time budget.")


@app.get("/", include_in_schema=False)
async def preview_home():
    return RedirectResponse(url="/api/docs", status_code=307)


@app.get("/api/docs", include_in_schema=False)
async def api_docs():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="SchemeRadar API")


@app.get("/api/openapi.json", include_in_schema=False)
async def api_schema():
    return app.openapi()




@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return error_response(request, exc.status_code, str(exc.detail))
