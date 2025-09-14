import datetime
import uuid
from typing import List, Optional
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.click import Click
from src.models.link import Link
from src.repositories.base import BaseRepository


class ClickRepository(BaseRepository):
    model = Click

    async def get_clicks_list(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        link_id: int,
        skip: int,
        limit: int,
    ) -> list[Click]:
        stmt = (
            select(self.model)
            .join(self.model.link)
            .where(Link.user_id == user_id, Link.id == link_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def aggregate_records(
        self,
        db: AsyncSession,
        column,
        filters: List,
        distinct_flag: bool = False,
        group_by=None,
        order_by=None,
        limit: int = None,
        key: str | None = None,
    ) -> List[dict]:
        expr = distinct(column) if distinct_flag else column

        if group_by is None:
            stmt = select(func.count(expr)).where(*filters)
            result = await db.execute(stmt)
            return result.scalar() or 0

        stmt = select(column, func.count(expr).label("count")).where(*filters)
        stmt = stmt.group_by(group_by)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)

        rows = (await db.execute(stmt)).all()
        key_name = key or getattr(column, "key", "value")
        return [
            {key_name: value, "count": count}
            for value, count in rows
            if value is not None
        ]
