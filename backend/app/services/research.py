"""Research orchestration policy, separate from HTTP and deterministic graph nodes."""
import logging

from psycopg import Error as DatabaseError
from psycopg_pool import PoolTimeout

from ..models import AgentRequest
from ..security import ServiceError


async def run_agent(services, request: AgentRequest):
    result = await services.workflow.run(request)
    if request.mode == "RESEARCH" and services.config.enable_research_history:
        try:
            result.research_id = await services.db.save_research(result)
        except (DatabaseError, PoolTimeout, ServiceError):
            logging.getLogger("schemeradar").warning("research_history_save_failed")
            result.errors.append("Research results are available, but research history could not be saved.")
    return result
