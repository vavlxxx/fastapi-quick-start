import os
import sys
import json
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.db import sessionmaker
from src.api import router as main_router
from src.api.docs import router as docs_router
from src.utils.db_manager import DBManager
from src.config import settings


def configurate_logging(root_logger_name: str) -> logging.Logger:
    basepath = Path(__file__).resolve().parent.parent
    with open(basepath / "logging_config.json", "r") as f:
        config = json.load(f)

    os.makedirs(basepath / "logs", exist_ok=True)
    logging.config.dictConfig(config)
    return logging.getLogger(root_logger_name)


logger = configurate_logging("src")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with DBManager(sessionmaker) as db:
        await db.check_connection()
        logger.info("Successfully connected to DB")

    logger.info("All checks passed!")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.TITLE,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    default_response_class=ORJSONResponse,
)
app.include_router(main_router)
app.include_router(docs_router)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.UVICORN_RELOAD,
    )
