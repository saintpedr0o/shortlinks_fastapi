from pydantic import BaseModel
from src.exceptions import (
    InvalidPasswordException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from src.repositories.user import UserRepository
import uuid
import bcrypt
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.schemas.user import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def authenticate_user(
        self, db: AsyncSession, login: str, password: str
    ) -> User:
        if "@" in login:
            user = await self._user_repository.get_by_email(db, login)
        else:
            user = await self._user_repository.get_by_username(db, login)

        if not user:
            raise UserNotFoundException("User not found")

        if not self.verify_password(password, user.hashed_password):
            raise InvalidPasswordException("Invalid password")

        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User:
        user = await self._user_repository.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundException(f"User with id '{user_id}' not found")
        return user

    async def get_users(
        self,
        db: AsyncSession,
        skip: int,
        limit: int,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> List[User]:
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        if is_superuser is not None:
            filters["is_superuser"] = is_superuser

        users = await self._user_repository.get_list_objs(
            db=db, skip=skip, limit=limit, **filters
        )
        return users or []

    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        if await self._user_repository.get_by_username(db, user_in.username):
            raise UserAlreadyExistsException("User with this username already exists")
        if await self._user_repository.get_by_email(db, user_in.email):
            raise UserAlreadyExistsException("User with this email already exists")

        hashed_password = bcrypt.hashpw(
            user_in.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        user = User(
            id=uuid.uuid4(),
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
        )
        return await self._user_repository.create_obj(db, user)

    async def update_user(
        self,
        db: AsyncSession,
        db_user: User,
        user_in: BaseModel,  # UserUpdate or UserAdminUpdate
    ) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        new_password = update_data.pop("password", None)

        if new_password:
            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            db_user.hashed_password = hashed_password

        for field, value in update_data.items():
            setattr(db_user, field, value)

        await self._user_repository.update_obj(db, db_user)
        return db_user

    async def deactivate_user(self, db: AsyncSession, db_user: User) -> None:
        db_user.is_active = False
        await self._user_repository.update_obj(db, db_user)

    async def delete_user(self, db: AsyncSession, user: User) -> None:
        await self._user_repository.delete_obj(db, user)
