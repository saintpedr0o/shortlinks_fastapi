import re
import time
from typing import Dict
import asyncpg
from src.config import get_settings

settings = get_settings()


def normalize_dsn(dsn: str) -> str:
    return re.sub(r"^(postgresql|postgres)\+[^:]+", r"\1", dsn)


async def check_db() -> Dict:
    try:
        start = time.perf_counter()
        dsn = normalize_dsn(settings.db_url_str)
        conn = await asyncpg.connect(dsn)
        await conn.execute("SELECT 1;")
        await conn.close()
        duration = time.perf_counter() - start
        return {"db_status": "ok", "db_resp_time": f"{round(duration * 1000, 2)} ms"}
    except Exception as e:
        print(e)
        return {"db_status": "error", "db_resp_time": "0.00 ms"}
