import logging
import subprocess

from fastapi import FastAPI
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
    # unnecessary code
    # DB migrations
    subprocess.run(["alembic", "upgrade", "head"])

    return app
