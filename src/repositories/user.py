import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        return await self.get_one_by_filters(db, id=user_id)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        return await self.get_one_by_filters(db, username=username)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await self.get_one_by_filters(db, email=email)
