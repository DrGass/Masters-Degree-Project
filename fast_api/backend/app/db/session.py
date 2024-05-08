from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

from env import get_env

env = get_env()

DB_URI = (
    f"postgresql://{env.postgres_user}:{env.postgres_password}@"
    f"{env.postgres_host}:{env.postgres_port}/{env.postgres_database}"
)
engine = create_engine(DB_URI)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBSession:
    def __init__(self):
        self.db = Session()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


async def get_db():
    with DBSession() as db:
        yield db
