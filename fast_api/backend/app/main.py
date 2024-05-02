import logging
import subprocess

from fastapi import FastAPI
from api.endpoints.data_loading import data_loading
from api.endpoints.database_lookup import database_lookup
from env import get_env


def create_app():
    env = get_env()

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    app = FastAPI(
        docs_url="/docs",
        redoc_url="/redoc",
        version="0.1.0",
        title="entrustment",
    )

    app.include_router(data_loading)
    app.include_router(database_lookup)
    # DB migrations
    subprocess.run(["alembic", "upgrade", "head"])

    return app
