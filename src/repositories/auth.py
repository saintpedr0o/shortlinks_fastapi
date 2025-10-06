from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.auth import RefreshToken
from src.repositories.base import BaseRepository
from uuid import UUID


class AuthRepository(BaseRepository):
    model = RefreshToken

    async def get_active_by_user(
        self, db: AsyncSession, user_id: UUID
    ) -> Optional[RefreshToken]:
        return await self.get_one_by_filters(db, user_id=user_id, revoked=False)

    async def get_by_jti(
        self, db: AsyncSession, jti: str, user_id: UUID
    ) -> Optional[RefreshToken]:
        return await self.get_one_by_filters(db, jti=jti, user_id=user_id)
