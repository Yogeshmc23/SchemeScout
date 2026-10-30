import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from psycopg import Error as DatabaseError
from psycopg_pool import PoolTimeout

from .config import settings
from .db import Database
from .eligibility import match
from .models import (
    AgentRequest,
    AgentResult,
    ExtractRequest,
    FetchRequest,
    FetchResult,
    Match,
    MatchRequest,
    Profile,
    Query,
    Scholarship,
    Source,
)
from .providers import Ollama, TinyFish
from .security import ServiceError, is_official
from .workflow import Workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
# Dependency loggers can include URLs or database connection details; avoid emitting them.
for name in ("httpx", "httpcore", "psycopg.pool", "mcp"):
    logging.getLogger(name).setLevel(logging.CRITICAL)
logger = logging.getLogger("schemeradar")
config = settings()
db = Database(config)
tinyfish, ollama = TinyFish(config), Ollama(config)
workflow = Workflow(db, tinyfish, ollama)
slots = asyncio.Semaphore(config.max_concurrent_workflows)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.open()
    yield
    await db.close()


app = FastAPI(title="SchemeRadar", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[config.frontend_origin], allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"], allow_credentials=False)


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
                return finish(JSONResponse(status_code=413, content={"detail": "Request body exceeds 256 KiB."}))
        request._body = bytes(body)
    expensive = request.method == "POST" and request.url.path in {
        "/api/agent", "/api/discover", "/api/research", "/api/chat", "/api/search", "/api/fetch", "/api/extract"
    }
    if expensive:
        try:
            await asyncio.wait_for(slots.acquire(), timeout=0.1)
        except TimeoutError:
            return finish(JSONResponse(status_code=429, content={"detail": "Research capacity is busy. Retry shortly."}))
    try:
        response = await call_next(request)
    finally:
        if expensive:
            slots.release()
    return finish(response)


@app.exception_handler(ServiceError)
async def service_error(request, exc):
    return JSONResponse(status_code=exc.code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Pydantic's default error includes rejected input; do not echo student data or content.
    errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logger.error("Unhandled application failure type=%s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Unexpected server error. Check backend service health."},
                        headers={"X-Request-ID": getattr(request.state, "request_id", uuid.uuid4().hex)})


@app.exception_handler(DatabaseError)
@app.exception_handler(PoolTimeout)
async def database_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": "PostgreSQL is unavailable or migrations have not been applied."})


@app.exception_handler(TimeoutError)
async def timeout_error(request, exc):
    return JSONResponse(status_code=504, content={"detail": "External service exceeded the request time budget."})


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


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "SchemeRadar"}


@app.get("/api/ready")
async def ready():
    await db.health()
    return {"database": "ready", "tinyfish_configured": bool(config.tinyfish_api_key),
            "ollama": "not probed; run a live model request to verify"}


@app.post("/api/profile", response_model=Profile)
async def profile(body: Profile):
    # Profiles are validated but deliberately not stored on the server.
    return body


@app.get("/api/scholarships", response_model=list[Scholarship])
async def scholarships():
    return await db.list()


@app.post("/api/search", response_model=list[Source])
async def search(body: Query):
    return await asyncio.wait_for(tinyfish.search(body.query), timeout=100)


@app.post("/api/fetch", response_model=FetchResult)
async def fetch(body: FetchRequest):
    pages, errors = await asyncio.wait_for(tinyfish.fetch([str(u) for u in body.urls]), timeout=100)
    return {"pages": pages, "errors": errors}


@app.post("/api/extract", response_model=Scholarship)
async def extract(body: ExtractRequest):
    # Refetch: never let caller-supplied content masquerade as verified official evidence.
    pages, _errors = await tinyfish.fetch([str(body.url)])
    if not pages:
        raise ServiceError("The source could not be fetched for extraction.", 502)
    return await ollama.extract(pages[0])


@app.post("/api/eligibility", response_model=list[Match])
async def stored_matching(body: Profile):
    records = await db.list()
    return [match(body, record.model_copy(update={
        "official_source": record.official_source and is_official(str(record.source_url))
    })) for record in records]


@app.post("/api/match", response_model=list[Match])
async def matching(body: MatchRequest):
    # Client-supplied records are never accepted as official confirmations.
    records = [s.model_copy(update={"official_source": False}) for s in body.scholarships]
    return [match(body.profile, s) for s in records]


async def run_agent(body: AgentRequest):
    return await workflow.run(body)


@app.post("/api/agent", response_model=AgentResult)
async def agent(body: AgentRequest):
    return await run_agent(body)


@app.post("/api/chat", response_model=AgentResult)
async def chat(body: Query):
    return await run_agent(AgentRequest(mode="CHAT", query=body.query))


@app.post("/api/research", response_model=AgentResult)
async def research(body: Query):
    return await run_agent(AgentRequest(mode="RESEARCH", query=body.query))


@app.post("/api/discover", response_model=AgentResult)
async def discover(body: AgentRequest):
    if body.mode != "DISCOVER":
        raise ServiceError("This endpoint requires mode DISCOVER.", 422)
    return await run_agent(body)
