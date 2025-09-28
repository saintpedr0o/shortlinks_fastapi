from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.db_url_str)
async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
