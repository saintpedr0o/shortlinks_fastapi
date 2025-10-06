from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import get_settings

settings = get_settings()


def get_engine(url: str | None = None):
    if url is None:
        url = settings.db_url_str
    return create_async_engine(url, echo=False)


def get_session_factory(engine=None):
    if engine is None:
        engine = get_engine()
    return async_sessionmaker(bind=engine, expire_on_commit=False)
