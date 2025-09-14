from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import Base
from sqlalchemy import select
from typing import List, Optional


class BaseRepository:
    model: type[Base]

    async def create_obj(self, db: AsyncSession, obj: Base) -> Base:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update_obj(self, db: AsyncSession, obj: Base) -> Base:
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete_obj(self, db: AsyncSession, obj: Base) -> None:
        await db.delete(obj)
        await db.commit()

    async def get_one_by_filters(self, db: AsyncSession, **filters) -> Optional[Base]:
        result = await db.execute(select(self.model).filter_by(**filters))
        return result.scalar_one_or_none()

    async def get_list_objs(
        self, db: AsyncSession, skip: int, limit: int, **filters
    ) -> List[Base]:
        stmt = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
