from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.link import Link
from src.repositories.base import BaseRepository


class LinkRepository(BaseRepository):
    model = Link

    async def get_by_original_link(
        self, db: AsyncSession, original_link: str, user_id: UUID
    ) -> Link | None:
        return await self.get_one_by_filters(
            db, original_link=original_link, user_id=user_id
        )

    async def get_user_links_list(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int,
        limit: int,
    ) -> List[Link]:
        return await self.get_list_objs(db, skip=skip, limit=limit, user_id=user_id)
