from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.models import AgentRequest, AgentResult
from app.security import ServiceError
from app.services.research import run_agent


@pytest.mark.parametrize('mode,enabled,save', [('RESEARCH', True, True), ('RESEARCH', False, False), ('CHAT', True, False)])
async def test_history_policy(mode, enabled, save):
    result = AgentResult(mode=mode)
    services = SimpleNamespace(config=SimpleNamespace(enable_research_history=enabled),
                               workflow=SimpleNamespace(run=AsyncMock(return_value=result)),
                               db=SimpleNamespace(save_research=AsyncMock(return_value='saved-id')))
    actual = await run_agent(services, AgentRequest(mode=mode, query='fixture query'))
    assert services.db.save_research.await_count == int(save)
    assert actual.research_id == ('saved-id' if save else None)


async def test_history_outage_preserves_valid_results_without_fake_save():
    result = AgentResult(mode='RESEARCH', summary='Real validated result', stored_count=1)
    services = SimpleNamespace(config=SimpleNamespace(enable_research_history=True),
                               workflow=SimpleNamespace(run=AsyncMock(return_value=result)),
                               db=SimpleNamespace(save_research=AsyncMock(side_effect=ServiceError('database unavailable'))))
    actual = await run_agent(services, AgentRequest(mode='RESEARCH', query='fixture query'))
    assert actual.summary == result.summary
    assert actual.stored_count == 1
    assert actual.research_id is None
    assert 'could not be saved' in actual.errors[0]
