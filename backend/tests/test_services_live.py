"""Opt-in real services test. Never substitutes fixtures for live providers."""
import os

import pytest

from app.config import Settings
from app.db import Database
from app.models import AgentRequest, Profile
from app.providers import Ollama, TinyFish
from app.workflow import Workflow


@pytest.mark.skipif(os.getenv("RUN_LIVE_SERVICES") != "1", reason="Requires RUN_LIVE_SERVICES=1 and live TinyFish/Ollama/PostgreSQL")
async def test_live_karnataka_discovery():
    config = Settings()
    assert config.database_url and config.tinyfish_api_key, "Configure services in backend environment"
    db = Database(config)
    await db.open()
    try:
        await db.health()
        result = await Workflow(db, TinyFish(config), Ollama(config)).run(AgentRequest(
            mode="DISCOVER", query="Karnataka engineering scholarships official eligibility application",
            profile=Profile(state="Karnataka", course="B.Tech", education_level="Undergraduate",
                            study_year=2, annual_income=250000, category="OBC"),
        ))
        assert result.sources, "Live Search returned no sources"
        assert result.scholarships, "No official page yielded a validated scholarship; inspect provider/source contracts"
        assert result.stored_count > 0 and result.matches
        stored = await db.list()
        assert any(str(s.source_url) == str(result.scholarships[0].source_url) for s in stored)
        answer = await Ollama(config).answer("What documents are required?", result.scholarships)
        assert answer.strip()
    finally:
        await db.close()
