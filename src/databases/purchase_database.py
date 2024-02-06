import asyncpg


class PurchaseDatabase:
    async def register_shipping(self, address: str, db: asyncpg.Connection) -> asyncpg.Record:
        query = """
            insert into shippings(address) values
            ($1)
            returning *;
        """
        shipping = await db.fetchrow(query, address)
        return shipping

    async def register_payment(self, card_number: str, cvv: str, db: asyncpg.Connection) -> asyncpg.Record:
        query = """
            insert into payments(card_number, cvv) values
            ($1, $2)
            returning *;
        """
        payment = await db.fetchrow(query, card_number, cvv)
        return payment

    async def register_receipt(
        self, total: float, user_id: int, shipping_id: int, payment_id: int, db: asyncpg.Connection
    ) -> asyncpg.Record:
        query = """
            insert into receipts(total, user_id, shipping_id, payment_id) values
            ($1, $2, $3, $4)
            returning *;
        """
        receipt = await db.fetchrow(query, total, user_id, shipping_id, payment_id)
        return receipt

    async def register_purchase(
        self, item_id: int, qty: int, receipt_id: int, db: asyncpg.Connection
    ) -> asyncpg.Record:
        query = """
            insert into purchases(item_id, qty, receipt_id) values
            ($1, $2, $3)
            returning *;
        """
        purchase = await db.fetchrow(query, item_id, qty, receipt_id)
        return purchase

    async def get_purchased_items_by_receipt(self, receipt_id: int, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select i.id, i.name, i.price, i.category, p.qty from receipts r
            join purchases p on r.id = p.receipt_id
            join items i on p.item_id = i.id
            where r.id = $1;
        """
        purchased_items = await db.fetch(query, receipt_id)
        return purchased_items

    async def get_receipt(self, receipt_id: int, db: asyncpg.Connection) -> asyncpg.Record | None:
        query = """
            select * from receipts where id = $1;
        """
        receipt = await db.fetchrow(query, receipt_id)
        return receipt

    async def get_user_receipts(self, user_id: int, db: asyncpg.Connection) -> list[asyncpg.Record]:
        query = """
            select * from receipts where user_id = $1;
        """
        receipts = await db.fetch(query, user_id)
        return receipts
