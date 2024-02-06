import asyncpg


class UserDatabase:
    async def register_user(self, username: str, password: str, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            insert into users(username, password) values
            ($1, $2)
            returning *;
        """
        user = await db.fetchrow(query, username, password)
        return user

    async def get_user(self, user_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select *
            from users
            where id = $1;
        """
        user = await db.fetchrow(query, user_id)
        return user

    async def verify_user(self, username: str, password: str, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select *
            from users
            where username = $1 and password = $2;
        """
        user = await db.fetchrow(query, username, password)
        return user

    async def reset_password(self, new_password: str, user_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            update users
            set password = $1
            where id = $2;
        """
        await db.execute(query, new_password, user_id)

    async def delete_user(self, user_id, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            delete from users
            where id = $1;
        """
        await db.execute(query, user_id)
