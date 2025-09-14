from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.user import UserService
from src.models import User
from src.exceptions import UserNotFoundException, UserAlreadyExistsException
from src.schemas.user import (
    UserAdminUpdate,
    UserCreate,
    UserOut,
    UserUpdate,
)
from src.api.dependencies import (
    get_active_user,
    get_db,
    superuser_required,
    get_user_service,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.register_user(db, user_create)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_active_user)):
    return current_user


@router.patch("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    user_service: UserService = Depends(get_user_service),
):
    updated_user = await user_service.update_user(db, current_user, user_in)
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_active_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.deactivate_user(db, current_user)
    return


# -------------------admin-------------------
admin_router = APIRouter(
    prefix="/users", tags=["Admin Users"], dependencies=[Depends(superuser_required)]
)


@admin_router.post(
    "/create",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.register_user(db, user_create)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@admin_router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    try:
        db_user = await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    updated_user = await user_service.update_user(db, db_user, user_in)
    return updated_user


@admin_router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found"
        )
    return user


@admin_router.get("/list", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=20),
    is_active: Optional[bool] = Query(None),
    is_superuser: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    users = await user_service.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        is_superuser=is_superuser,
    )
    return users


@admin_router.delete("/deactivate/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    try:
        db_user = await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await user_service.deactivate_user(db, db_user)
    return


@admin_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    try:
        db_user = await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await user_service.delete_user(db, db_user)
    return
