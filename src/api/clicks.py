from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_active_user, get_click_service, get_db
from src.exceptions import ClicksNotFoundException
from src.models.user import User
from src.schemas.click import ClickOut, ClicksByPeriodItem, StatsOut
from src.services.click import ClickService

router = APIRouter(
    prefix="/clicks",
    tags=["Clicks, Stats"],
)


@router.get("/{link_id}", status_code=status.HTTP_200_OK, response_model=List[ClickOut])
async def get_link_clicks(
    link_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    click_service: ClickService = Depends(get_click_service),
):
    try:
        clicks = await click_service.get_link_clicks(
            db, user_id=current_user.id, link_id=link_id, skip=skip, limit=limit
        )
    except ClicksNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return clicks


@router.get("/stats/{link_id}", status_code=status.HTTP_200_OK, response_model=StatsOut)
async def get_summary_stats(
    link_id: int,
    date_from: date | None = Query(None, description="From (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="To (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    click_service: ClickService = Depends(get_click_service),
):
    return await click_service.get_summary(
        db, current_user.id, link_id=link_id, date_from=date_from, date_to=date_to
    )


@router.get(
    "/period/{link_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ClicksByPeriodItem],
)
async def get_clicks_by_period(
    link_id: int,
    date_from: date = Query(..., description="From (YYYY-MM-DD)"),
    date_to: date = Query(..., description="To (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    click_service: ClickService = Depends(get_click_service),
):
    return await click_service.get_period_clicks(
        db, current_user.id, link_id=link_id, date_from=date_from, date_to=date_to
    )
