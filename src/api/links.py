from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.api.dependencies import (
    get_active_user,
    get_db,
    get_link_service,
)
from src.models.user import User
from src.schemas.link import BaseLink, LinkCreate, LinkListOut, LinkOut
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.link import (
    LinkAlreadyExistsException,
    LinkService,
    LinkNotFoundException,
)

router = APIRouter(prefix="/links", tags=["Links"])


@router.post("/create", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
async def create_short_link(
    link_create: LinkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    link_service: LinkService = Depends(get_link_service),
):
    try:
        return await link_service.create_link(db, link_create, current_user.id)
    except LinkAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/all",
    response_model=List[LinkListOut],
    status_code=status.HTTP_200_OK,
)
async def get_links(
    skip: int = 0,
    limit: int = Query(5, ge=0, le=5),
    db: AsyncSession = Depends(get_db),
    link_service: LinkService = Depends(get_link_service),
    current_user: User = Depends(get_active_user),
):
    return await link_service.get_user_links(db, current_user.id, skip, limit)


@router.get(
    "/info/{short_code}",
    response_model=LinkOut,
    status_code=status.HTTP_200_OK,
)
async def get_link_by_code(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    link_service: LinkService = Depends(get_link_service),
):
    try:
        return await link_service.get_by_short_code(db, short_code, current_user.id)
    except LinkNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_links_by_original_link(
    base_link: BaseLink,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    link_service: LinkService = Depends(get_link_service),
):
    try:
        await link_service.delete_link(
            db, str(base_link.original_link), current_user.id
        )
    except LinkNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
