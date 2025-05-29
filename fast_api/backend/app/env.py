from pydantic_settings import BaseSettings
from functools import lru_cache


class Env(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"

    postgres_user: str
    postgres_password: str
    postgres_database: str
    postgres_host: str
    postgres_port: int
    postgres_image_tag: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_env():
    return Env()
