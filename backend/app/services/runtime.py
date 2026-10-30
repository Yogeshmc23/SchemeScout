"""Application-scoped dependencies; one pool, provider pair and graph per app."""
import asyncio
from dataclasses import dataclass

from ..config import Settings
from ..db import Database
from ..tools.tinyfish import TinyFish
from ..workflow import Workflow
from .ollama import Ollama


@dataclass
class Services:
    config: Settings
    db: Database
    tinyfish: TinyFish
    ollama: Ollama
    workflow: Workflow
    slots: asyncio.Semaphore

    @classmethod
    def create(cls, config: Settings):
        db = Database(config)
        tinyfish, ollama = TinyFish(config), Ollama(config)
        return cls(config, db, tinyfish, ollama, Workflow(db, tinyfish, ollama),
                   asyncio.Semaphore(config.max_concurrent_workflows))
