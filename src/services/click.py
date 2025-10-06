from collections import Counter
from datetime import date, datetime, time, timezone
from typing import Dict, List
from sqlalchemy import func
from src.exceptions import ClicksNotFoundException
from src.models.link import Link
from src.repositories.click import ClickRepository
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.click import Click
from user_agents import parse


class ClickService:
    def __init__(self, click_repository: ClickRepository):
        self._click_repository = click_repository

    async def register_click(self, db, link_id, ip_address, user_agent, referrer):
        click = Click(
            link_id=link_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
        )
        return await self._click_repository.create_obj(db, click)

    async def get_link_clicks(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        link_id: int,
        skip: int,
        limit: int,
    ) -> List[Click]:

        clicks = await self._click_repository.get_clicks_list(
            db, user_id=user_id, link_id=link_id, skip=skip, limit=limit
        )
        if not clicks:
            raise ClicksNotFoundException(f"No clicks found for link_id={link_id}")
        return clicks

    async def get_summary(
        self,
        db: AsyncSession,
        user_id: int,
        link_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Dict:
        filters = [Click.link_id == link_id, Link.user_id == user_id]

        if date_from:
            filters.append(
                Click.clicked_at
                >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
            )
        if date_to:
            filters.append(
                Click.clicked_at
                <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)
            )

        total_clicks = await self._click_repository.aggregate_records(
            db=db, column=Click.id, filters=filters
        )

        today = datetime.now(timezone.utc).date()
        today_filters = [
            Click.link_id == link_id,
            Link.user_id == user_id,
            Click.clicked_at >= datetime.combine(today, time.min, tzinfo=timezone.utc),
            Click.clicked_at <= datetime.combine(today, time.max, tzinfo=timezone.utc),
        ]

        today_clicks = await self._click_repository.aggregate_records(
            db=db, column=Click.id, filters=today_filters
        )

        unique_ips = await self._click_repository.aggregate_records(
            db=db, column=Click.user_agent, filters=filters, distinct_flag=True
        )

        unique_referrers = await self._click_repository.aggregate_records(
            db=db, column=Click.referrer, filters=filters, distinct_flag=True
        )

        top_referrers = await self._click_repository.aggregate_records(
            db=db,
            column=Click.referrer,
            filters=filters,
            group_by=Click.referrer,
            order_by=func.count(Click.referrer).desc(),
            limit=5,
            key="referrer",
        )
        brows = await self._click_repository.aggregate_records(
            db=db,
            column=Click.user_agent,
            filters=filters,
            group_by=Click.user_agent,
            order_by=func.count(Click.user_agent),
        )
        counter = Counter()
        for row in brows:
            ua = row["user_agent"]
            if not ua:
                continue
            browser = parse(ua).browser.family
            counter[browser] += row["count"]

        browsers = dict(counter.most_common(5))

        return {
            "total_clicks": total_clicks,
            "today_clicks": today_clicks,
            "unique_ips": unique_ips,
            "unique_referrers": unique_referrers,
            "top_referrers": top_referrers,
            "browsers": browsers,
        }

    async def get_period_clicks(
        self,
        db: AsyncSession,
        user_id: int,
        link_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Dict:
        filters = [Click.link_id == link_id, Link.user_id == user_id]

        if date_from:
            filters.append(
                Click.clicked_at
                >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
            )
        if date_to:
            filters.append(
                Click.clicked_at
                <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)
            )

        clicks_by_period = await self._click_repository.aggregate_records(
            db,
            column=func.date_trunc("day", Click.clicked_at).label("period"),
            filters=filters,
            group_by="period",
            order_by="period",
            key="period",
        )

        for row in clicks_by_period:
            row["period"] = row["period"].date().isoformat()

        return {"clicks_by_period": clicks_by_period}
