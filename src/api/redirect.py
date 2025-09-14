from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_click_service, get_db, get_link_service
from src.exceptions import LinkNotFoundException
from src.services.click import ClickService
from src.services.link import LinkService
from src.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_link(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    link_service: LinkService = Depends(get_link_service),
    click_service: ClickService = Depends(get_click_service),
):
    try:
        link = await link_service.get_by_short_code_public(db, short_code)
    except LinkNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if settings.enable_tracking:
        await click_service.register_click(
            db,
            link_id=link.id,
            ip_address=(
                request.headers.get("X-Forwarded-For", request.client.host)
                if request.client and settings.log_ip_address
                else None
            ),
            user_agent=(
                request.headers.get("user-agent") if settings.log_user_agent else None
            ),
            referrer=(
                request.headers.get("referer") if settings.log_referrer else None
            ),
        )

    return RedirectResponse(url=link.original_link)
