from typing import AsyncGenerator

import pytest

from src.db import sessionmaker_null_pool, engine_null_pool
from src.api.v1.dependencies.db import get_db_with_null_pool
from src.config import settings
from src.utils.db_manager import DBManager
from src.models import *  # noqa: F403
from src.models.base import Base


@pytest.fixture()
async def db() -> AsyncGenerator[DBManager, None]:
    async for db in get_db_with_null_pool():
        yield db


@pytest.fixture(scope="module")
async def db_module() -> AsyncGenerator[DBManager, None]:
    async for db in get_db_with_null_pool():
        yield db


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode() -> None:
    assert settings.MODE == "TEST"
    assert settings.DB_NAME == "test_db"


@pytest.fixture(scope="session", autouse=True)
async def main(check_test_mode) -> None:
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with DBManager(session_factory=sessionmaker_null_pool) as db:
        await db.check_connection()
