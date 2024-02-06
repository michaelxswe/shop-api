import asyncpg
from databases.user_database import UserDatabase
from fastapi import Depends
from models import UserModel


class UserService:
    def __init__(self, user_database: UserDatabase = Depends()):
        self.user_database = user_database

    async def register_user(self, username: str, password: str, db: asyncpg.Connection) -> UserModel:
        user = await self.user_database.register_user(username=username, password=password, db=db)
        return UserModel(**dict(user))  # type: ignore

    async def get_user(self, user_id: int, db: asyncpg.Connection) -> UserModel | None:
        user = await self.user_database.get_user(user_id=user_id, db=db)

        if not user:
            return None

        return UserModel(**dict(user))

    async def verify_user(self, username: str, password: str, db: asyncpg.Connection) -> UserModel | None:
        user = await self.user_database.verify_user(username=username, password=password, db=db)

        if not user:
            return None

        return UserModel(**dict(user))

    async def verify_password(self, user_id: int, password, db: asyncpg.Connection):
        user_model = await self.get_user(user_id=user_id, db=db)
        if not user_model:
            return False

        return user_model.password == password

    async def reset_password(self, new_password: str, user_id: int, db: asyncpg.Connection) -> None:
        await self.user_database.reset_password(new_password=new_password, user_id=user_id, db=db)

    async def delete_user(self, user_id: int, db: asyncpg.Connection) -> None:
        await self.user_database.delete_user(user_id=user_id, db=db)
