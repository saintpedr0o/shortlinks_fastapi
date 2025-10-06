from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from src.utils.monitoring import check_db

router = APIRouter(tags=["Monitoring"])


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness():
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/health")
async def readiness():
    db_status = await check_db()
    overall = "ok" if db_status["db_status"] == "ok" else "degraded"
    code = (
        status.HTTP_200_OK if overall == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(
        status_code=code,
        content={
            "status": overall,
            "details": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
