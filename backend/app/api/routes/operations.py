import asyncio
from uuid import UUID

from fastapi import APIRouter, Path
from fastapi import Query as QueryParameter

from ...eligibility import match
from ...models import (
    AgentRequest,
    AgentResult,
    ExtractionSnapshot,
    ExtractRequest,
    FetchRequest,
    FetchResult,
    Match,
    MatchRequest,
    Profile,
    Query,
    ResearchRun,
    Scholarship,
    Source,
)
from ...security import ServiceError, is_official
from ...services.research import run_agent as execute_agent
from ..dependencies import ServiceDependency
from ..errors import ErrorResponse

router = APIRouter(responses={status: {"model": ErrorResponse} for status in (404, 413, 422, 429, 500, 502, 503, 504)})


@router.get("/health")
async def health(services: ServiceDependency):
    return {"status": "ok", "service": "SchemeRadar"}


@router.get("/ready")
async def ready(services: ServiceDependency):
    await services.db.health()
    return {"database": "ready", "tinyfish_configured": bool(services.config.tinyfish_api_key),
            "ollama": "not probed; run a live model request to verify"}


@router.post("/profile", response_model=Profile)
async def profile(body: Profile, services: ServiceDependency):
    # Profiles are validated but deliberately not stored on the server.
    return body


@router.get("/scholarships", response_model=list[Scholarship])
async def scholarships(services: ServiceDependency):
    return await services.db.list()


@router.post("/search", response_model=list[Source])
async def search(body: Query, services: ServiceDependency):
    return await asyncio.wait_for(services.tinyfish.search(body.query), timeout=100)


@router.post("/fetch", response_model=FetchResult)
async def fetch(body: FetchRequest, services: ServiceDependency):
    pages, errors = await asyncio.wait_for(services.tinyfish.fetch([str(u) for u in body.urls]), timeout=100)
    return {"pages": pages, "errors": errors}


@router.post("/extract", response_model=Scholarship)
async def extract(body: ExtractRequest, services: ServiceDependency):
    # Refetch: never let caller-supplied content masquerade as verified official evidence.
    pages, _errors = await services.tinyfish.fetch([str(body.url)])
    if not pages:
        raise ServiceError("The source could not be fetched for extraction.", 502)
    return await services.ollama.extract(pages[0])


@router.post("/eligibility", response_model=list[Match])
async def stored_matching(body: Profile, services: ServiceDependency):
    records = await services.db.list()
    return [match(body, record.model_copy(update={
        "official_source": record.official_source and is_official(str(record.source_url))
    })) for record in records]


@router.post("/match", response_model=list[Match])
async def matching(body: MatchRequest, services: ServiceDependency):
    # Client-supplied records are never accepted as official confirmations.
    records = [s.model_copy(update={"official_source": False}) for s in body.scholarships]
    return [match(body.profile, s) for s in records]


async def run_agent(body: AgentRequest, services: ServiceDependency):
    return await execute_agent(services, body)


@router.post("/agent", response_model=AgentResult)
async def agent(body: AgentRequest, services: ServiceDependency):
    return await run_agent(body, services)


@router.post("/chat", response_model=AgentResult)
async def chat(body: Query, services: ServiceDependency):
    return await run_agent(AgentRequest(mode="CHAT", query=body.query), services)


@router.post("/research", response_model=AgentResult)
async def research(body: Query, services: ServiceDependency):
    return await run_agent(AgentRequest(mode="RESEARCH", query=body.query), services)


@router.post("/discover-and-match", response_model=AgentResult)
@router.post("/discover", response_model=AgentResult)
async def discover(body: AgentRequest, services: ServiceDependency):
    if body.mode != "DISCOVER":
        raise ServiceError("This endpoint requires mode DISCOVER.", 422)
    return await run_agent(body, services)


@router.get("/scholarships/{scholarship_id}", response_model=Scholarship)
async def scholarship_detail(services: ServiceDependency, scholarship_id: int = Path(gt=0, le=9_223_372_036_854_775_807)):
    record = await services.db.by_id(scholarship_id)
    if record is None:
        raise ServiceError("Scholarship not found.", 404)
    return record


@router.get("/scholarships/{scholarship_id}/history", response_model=list[ExtractionSnapshot])
async def scholarship_history(services: ServiceDependency, scholarship_id: int = Path(gt=0, le=9_223_372_036_854_775_807),
                              limit: int = QueryParameter(20, ge=1, le=50)):
    if await services.db.by_id(scholarship_id) is None:
        raise ServiceError("Scholarship not found.", 404)
    return await services.db.extraction_history(scholarship_id, limit)


@router.get("/research/history", response_model=list[ResearchRun])
async def research_history(services: ServiceDependency, limit: int = QueryParameter(10, ge=1, le=20)):
    if not services.config.enable_research_history:
        raise ServiceError("Research history is disabled for privacy. Enable ENABLE_RESEARCH_HISTORY on a trusted deployment.", 503)
    return await services.db.research_history(limit)


@router.get("/research/history/{identifier}", response_model=AgentResult)
async def research_detail(identifier: UUID, services: ServiceDependency):
    if not services.config.enable_research_history:
        raise ServiceError("Research history is disabled for privacy.", 503)
    result = await services.db.research_detail(identifier)
    if result is None:
        raise ServiceError("Research run not found.", 404)
    return result
