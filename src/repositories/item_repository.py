import asyncpg


class ItemRepository:
    async def register_item(
        self, name: str, price: float, category: str, qty: int, db: asyncpg.Connection
    ) -> asyncpg.Record:
        query = """
            insert into items(name, price, category, qty) values ($1, $2, $3, $4)
            returning *;
        """
        item = await db.fetchrow(query, name, price, category, qty)
        return item

    async def get_item(self, item_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select * from items
            where id = $1;
        """
        item = await db.fetchrow(query, item_id)
        return item

    async def increase_qty(self, item_id: int, qty: int, db: asyncpg.Connection) -> None:
        query = """
            update items
            set qty = qty + $1
            where id = $2
        """
        await db.execute(query, qty, item_id)

    async def decrease_qty(self, item_id: int, qty: int, db: asyncpg.Connection) -> None:
        query = """
            update items
            set qty = qty - $1
            where id = $2;
        """
        await db.execute(query, qty, item_id)

    async def remove_item(self, item_id: int, db: asyncpg.Connection) -> None:
        query = """
            delete from items where id = $1;
        """
        await db.execute(query, item_id)

    async def get_all_items(self, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select * from items;
        """
        items = await db.fetch(query)
        return items

    async def get_items_by_category(self, category: str, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select * from items
            where category = $1;
        """
        items = await db.fetch(query, category)
        return items

    async def register_item_rating(self, item_id: int, rating: int, db: asyncpg.Connection) -> None:
        query = """
            insert into item_ratings(item_id, rating) values
            ($1, $2);
        """
        await db.execute(query, item_id, rating)

    async def get_item_ratings(self, item_id: int, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select * from item_ratings where item_id = $1
        """
        item_ratings = await db.fetch(query, item_id)
        return item_ratings
