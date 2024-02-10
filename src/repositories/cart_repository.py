import asyncpg


class CartRepository:
    async def get_item(self, item_id: int, user_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select * from carts
            where item_id = $1 and user_id = $2;
        """
        item = await db.fetchrow(query, item_id, user_id)
        return item

    async def increase_qty(self, item_id: int, qty: int, user_id: int, db: asyncpg.Connection) -> None:
        query = """
            update carts
            set qty = qty + $1
            where item_id = $2 and user_id = $3;
        """
        await db.execute(query, qty, item_id, user_id)

    async def decrease_qty(self, item_id: int, qty: int, user_id: int, db: asyncpg.Connection) -> None:
        query = """
            update carts
            set qty = qty - $1
            where item_id = $2 and user_id = $3;
        """
        await db.execute(query, qty, item_id, user_id)

    async def add_item(self, item_id: int, qty: int, user_id: int, db: asyncpg.Connection) -> None:
        query = """
            insert into carts(item_id, qty, user_id) values
            ($1, $2, $3);
        """
        await db.execute(query, item_id, qty, user_id)

    async def remove_item(self, item_id: int, user_id: int, db: asyncpg.Connection) -> None:
        query = """
            delete from carts
            where item_id = $1 and user_id = $2;
        """
        await db.execute(query, item_id, user_id)

    async def clear_cart(self, user_id: int, db: asyncpg.Connection) -> None:
        query = """
            delete from carts
            where user_id = $1;
        """
        await db.execute(query, user_id)

    async def clean_up(self, item_id: int, user_id: int, db: asyncpg.Connection) -> None:
        query = """
            delete from carts
            where item_id = $1 and user_id = $2 and qty <= 0;
        """
        await db.execute(query, item_id, user_id)

    async def get_cart(self, user_id: int, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select i.id, i.name, i.price, i.category, c.qty from carts c
            join items i on c.item_id = i.id
            where c.user_id = $1;
        """
        cart = await db.fetch(query, user_id)
        return cart

    async def get_total(self, user_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select sum(i.price * c.qty) as total from carts c
            join items i on c.item_id = i.id
            where c.user_id = $1
            group by c.user_id;
        """
        total = await db.fetchrow(query, user_id)
        return total
