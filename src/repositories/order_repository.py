import asyncpg


class OrderRepository:
    async def register_shipping_detail(self, address: str, db: asyncpg.Connection) -> asyncpg.Record:
        query = """
            insert into shipping_details(address) values
            ($1)
            returning *;
        """
        shipping_detail = await db.fetchrow(query, address)
        return shipping_detail

    async def register_payment_detail(self, card_number: str, cvv: str, db: asyncpg.Connection) -> asyncpg.Record:
        query = """
            insert into payment_details(card_number, cvv) values
            ($1, $2)
            returning *;
        """
        payment_detail = await db.fetchrow(query, card_number, cvv)
        return payment_detail

    async def register_order(
        self, total: float, user_id: int, shipping_detail_id: int, payment_detail_id: int, db: asyncpg.Connection
    ) -> asyncpg.Record:
        query = """
            insert into orders(total, user_id, shipping_detail_id, payment_detail_id) values
            ($1, $2, $3, $4)
            returning *;
        """
        order = await db.fetchrow(query, total, user_id, shipping_detail_id, payment_detail_id)
        return order

    async def register_order_detail(
        self, item_id: int, qty: int, order_id: int, db: asyncpg.Connection
    ) -> asyncpg.Record:
        query = """
            insert into order_details(item_id, qty, order_id) values
            ($1, $2, $3)
            returning *;
        """
        order_detail = await db.fetchrow(query, item_id, qty, order_id)
        return order_detail

    async def get_order_items(self, order_id: int, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select i.id, i.name, i.price, i.category, od.qty from orders o
            join order_details od on o.id = od.order_id
            join items i on od.item_id = i.id
            where o.id = $1;
        """
        order_details = await db.fetch(query, order_id)
        return order_details

    async def get_order(self, order_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select * from orders where id = $1;
        """
        order = await db.fetchrow(query, order_id)
        return order

    async def get_user_orders(self, user_id: int, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select * from orders where user_id = $1;
        """
        orders = await db.fetch(query, user_id)

        return orders
