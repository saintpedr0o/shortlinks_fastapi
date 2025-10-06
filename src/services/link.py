from typing import List
from uuid import UUID
from src.exceptions import LinkAlreadyExistsException, LinkNotFoundException
from src.repositories.link import LinkRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.link import Link
from src.schemas.link import LinkCreate
from src.utils.link_shortener import gen_short_code


class LinkService:
    def __init__(self, link_repository: LinkRepository):
        self._link_repository = link_repository

    async def create_link(
        self, db: AsyncSession, link_in: LinkCreate, user_id: UUID
    ) -> Link:

        existing = await self._link_repository.get_by_original_link(
            db, str(link_in.original_link), user_id
        )
        if existing:
            return existing

        for _ in range(5):
            short_code = gen_short_code()
            if not await self._link_repository.get_one_by_filters(
                db, short_code=short_code
            ):
                break
        else:
            raise LinkAlreadyExistsException(
                "Cannot generate unique short code, try again"
            )

        link = Link(
            original_link=str(link_in.original_link),
            short_code=short_code,
            user_id=user_id,
        )

        return await self._link_repository.create_obj(db, link)

    async def get_by_short_code(
        self,
        db: AsyncSession,
        short_code: str,
        user_id: UUID,
    ) -> Link:
        result = await self._link_repository.get_one_by_filters(
            db, short_code=short_code, user_id=user_id
        )
        if not result:
            raise LinkNotFoundException(f"Short code '{short_code}' not found")
        return result

    async def get_by_short_code_public(
        self, db: AsyncSession, short_code: str
    ) -> Link | None:
        """For redirect"""
        result = await self._link_repository.get_one_by_filters(
            db, short_code=short_code
        )
        if not result:
            raise LinkNotFoundException(f"Short code '{short_code}' not found")
        return result

    async def get_user_links(
        self, db: AsyncSession, user_id: UUID, skip: int, limit: int
    ) -> List[Link]:
        return (
            await self._link_repository.get_user_links_list(
                db, skip=skip, limit=limit, user_id=user_id
            )
            or []
        )

    async def delete_link(self, db: AsyncSession, link: str, user_id: UUID) -> None:
        link_obj = await self._link_repository.get_by_original_link(
            db, original_link=link, user_id=user_id
        )
        if not link_obj:
            raise LinkNotFoundException(f"Link '{link}' not found")
        await self._link_repository.delete_obj(db, link_obj)
