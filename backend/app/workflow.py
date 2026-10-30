import asyncio
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .db import Database
from .eligibility import match
from .models import AgentRequest, AgentResult, Page, Source, SourceOutcome
from .providers import Ollama, TinyFish
from .security import ServiceError, is_official, safe_url


class State(TypedDict):
    request: AgentRequest
    result: AgentResult
    pages: list[Page]
    detail_candidates: list[str]


class Workflow:
    """Explicit, bounded LangGraph pipeline, not an autonomous reasoning agent."""

    def __init__(self, db: Database, tinyfish: TinyFish, ollama: Ollama):
        self.db, self.tinyfish, self.ollama = db, tinyfish, ollama
        graph = StateGraph(State)
        for name in ("search", "fetch", "extract", "detail_fetch", "detail_extract", "store", "match", "chat", "summarize"):
            graph.add_node(name, getattr(self, name))
        graph.add_conditional_edges(START, lambda s: "chat" if s["request"].mode == "CHAT" else "search")
        graph.add_edge("search", "fetch")
        graph.add_edge("fetch", "extract")
        graph.add_conditional_edges("extract", lambda s: "detail_fetch" if s["detail_candidates"] else "store")
        graph.add_edge("detail_fetch", "detail_extract")
        graph.add_edge("detail_extract", "store")
        graph.add_conditional_edges("store", lambda s: "match" if s["request"].mode == "DISCOVER" else "summarize")
        graph.add_edge("match", "summarize")
        graph.add_edge("summarize", END)
        graph.add_edge("chat", END)
        self.graph = graph.compile()

    async def search(self, state):
        result = state["result"]
        result.sources = await self.tinyfish.search(state["request"].query)
        result.steps.append("Searched TinyFish for scholarship sources")
        if not result.sources:
            result.errors.append("Search returned no usable sources.")
        return {"result": result}

    async def fetch_pages(self, urls, result: AgentResult, stage: str):
        pages = []
        for url in urls:
            try:
                fetched, errors = await self.tinyfish.fetch([url])
                # Defense in depth: never accept a provider page under a different source URL.
                fetched = [p for p in fetched if safe_url(str(p.url)) == safe_url(url)]
                pages.extend(fetched)
                result.errors.extend(errors)
                result.source_outcomes.append(SourceOutcome(
                    url=url, stage=stage, status="SUCCESS" if fetched else "FAILED",
                    message="Fetched official page content" if fetched else "No successful page content returned",
                ))
            except ServiceError as exc:
                result.errors.append(exc.message)
                result.source_outcomes.append(SourceOutcome(url=url, stage=stage, status="FAILED", message=exc.message))
        result.steps.append(f"{stage}: fetched {len(pages)} of {len(urls)} approved pages")
        return pages

    async def fetch(self, state):
        result = state["result"]
        urls = list(dict.fromkeys(str(s.url) for s in result.sources if s.official and is_official(str(s.url))))[:3]
        if not urls:
            result.errors.append("No approved official domains found; third-party results were not used as confirmation.")
        return {"pages": await self.fetch_pages(urls, result, "FETCH"), "result": result}

    async def extract_pages(self, pages, result: AgentResult, stage: str):
        failed_pages = []
        for page in pages:
            try:
                record = await self.ollama.extract(page)
                identity = (str(record.source_url), record.name.casefold())
                if not any((str(s.source_url), s.name.casefold()) == identity for s in result.scholarships):
                    result.scholarships.append(record)
                result.source_outcomes.append(SourceOutcome(url=page.url, stage=stage, status="SUCCESS",
                                                            message=f"Validated extraction: {record.name}"))
            except ServiceError as exc:
                failed_pages.append(page)
                result.errors.append(exc.message)
                result.source_outcomes.append(SourceOutcome(url=page.url, stage=stage, status="FAILED", message=exc.message))
        return failed_pages

    async def extract(self, state):
        result = state["result"]
        failed = await self.extract_pages(state["pages"], result, "EXTRACT")
        visited = {safe_url(str(p.url)) for p in state["pages"]}
        candidates = []
        # One extra hop only, three detail URLs total, all from actual provider-returned links.
        for page in failed:
            for link in page.links:
                try:
                    url = safe_url(str(link), official_only=True)
                except ServiceError:
                    continue
                if url not in visited and url not in candidates and re.search(
                    r"scholarship|scheme|eligib|guideline|notification|application", url, re.IGNORECASE
                ):
                    candidates.append(url)
        result.steps.append(f"Validated {len(result.scholarships)} initial scholarship extractions")
        return {"result": result, "detail_candidates": candidates[:3]}

    async def detail_fetch(self, state):
        result = state["result"]
        urls = state["detail_candidates"]
        for url in urls:
            if not any(str(s.url) == url for s in result.sources):
                result.sources.append(Source(title="Linked scholarship detail page", url=url, official=True))
        pages = await self.fetch_pages(urls, result, "DETAIL_FETCH")
        return {"pages": pages, "result": result}

    async def detail_extract(self, state):
        result = state["result"]
        await self.extract_pages(state["pages"], result, "DETAIL_EXTRACT")
        return {"result": result}

    async def store(self, state):
        result = state["result"]
        persisted = []
        for scholarship in result.scholarships:
            await self.db.save(scholarship)
            stored = await self.db.get(str(scholarship.source_url), scholarship.name)
            if stored is None:
                raise ServiceError("A committed scholarship could not be retrieved. Retry after checking PostgreSQL.", 503)
            persisted.append(stored)
            result.stored_count += 1
        result.scholarships = persisted
        result.steps.append(f"Committed and reloaded {result.stored_count} records from PostgreSQL")
        return {"result": result}

    async def match(self, state):
        result = state["result"]
        result.matches = [match(state["request"].profile, s) for s in result.scholarships]
        result.steps.append("Evaluated explicit eligibility rules deterministically against retrieved records")
        return {"result": result}

    async def summarize(self, state):
        result = state["result"]
        fetched = sum(o.stage in {"FETCH", "DETAIL_FETCH"} and o.status == "SUCCESS" for o in result.source_outcomes)
        result.summary = (
            f"Discovered {len(result.sources)} sources; fetched {fetched} pages; "
            f"stored and reloaded {result.stored_count} scholarship records. "
            "Review source evidence and missing requirements before applying."
        )
        # Only factual fields already validated against source text; no invented research narrative.
        for record in result.scholarships:
            result.summary += f"\n\n{record.name}: {record.description or 'Description not stated in the source.'}"
        return {"result": result}

    async def chat(self, state):
        result = state["result"]
        records = await self.db.list(30)
        words = set(re.findall(r"[\w]+", state["request"].query.casefold())) - {
            "what", "which", "are", "the", "for", "and", "about", "how", "can", "you", "tell", "scholarships", "scholarship",
        }
        scored = [(len(words & set(re.findall(r"[\w]+", (s.name + " " + (s.description or "")).casefold()))), s) for s in records]
        selected = [s for score, s in sorted(scored, key=lambda pair: pair[0], reverse=True) if score > 0][:4]
        # Questions about documents/benefits can refer to the latest researched records explicitly.
        if not selected and words & {"documents", "benefits", "deadline", "deadlines", "found", "researched", "results"}:
            selected = records[:4]
        result.summary = await self.ollama.answer(state["request"].query, selected)
        result.sources = [Source(title=s.name, url=s.source_url, official=is_official(str(s.source_url))) for s in selected]
        result.steps.append(f"Retrieved {len(selected)} evidence records; eligibility was not decided by the assistant")
        return {"result": result}

    async def run(self, request: AgentRequest):
        try:
            # Preflight and graph share one whole-request budget, including provider initialization.
            async with asyncio.timeout(360):
                await self.db.health()
                state = await self.graph.ainvoke({
                    "request": request, "result": AgentResult(mode=request.mode, query=request.query),
                    "pages": [], "detail_candidates": [],
                })
                return state["result"]
        except TimeoutError:
            raise ServiceError("Research exceeded the time budget. Some records may already have been committed.", 504) from None
