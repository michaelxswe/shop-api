import asyncpg
from fastapi import Depends
from models import (
    ItemModel,
    OrderDetailModel,
    OrderModel,
    OrderSummaryModel,
    PaymentDetailModel,
    ShippingDetailModel,
)
from repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, order_repository: OrderRepository = Depends()):
        self.order_repository = order_repository

    async def register_shipping_detail(self, address: str, db: asyncpg.Connection) -> ShippingDetailModel:
        shipping_detail = await self.order_repository.register_shipping_detail(address=address, db=db)
        return ShippingDetailModel(**dict(shipping_detail))

    async def register_payment_detail(self, card_number: str, cvv: str, db: asyncpg.Connection) -> PaymentDetailModel:
        payment_detail = await self.order_repository.register_payment_detail(card_number=card_number, cvv=cvv, db=db)
        return PaymentDetailModel(**dict(payment_detail))

    async def register_order(
        self, total: float, user_id: int, shipping_detail_id: int, payment_detail_id: int, db: asyncpg.Connection
    ) -> OrderModel:
        order = await self.order_repository.register_order(
            total=total,
            user_id=user_id,
            shipping_detail_id=shipping_detail_id,
            payment_detail_id=payment_detail_id,
            db=db,
        )

        return OrderModel(**dict(order))

    async def register_order_detail(
        self, item_id: int, qty: int, order_id: int, db: asyncpg.Connection
    ) -> OrderDetailModel:
        order_detail = await self.order_repository.register_order_detail(
            item_id=item_id, qty=qty, order_id=order_id, db=db
        )
        return OrderDetailModel(**dict(order_detail))

    async def get_order(self, order_id: int, db: asyncpg.Connection) -> OrderModel | None:
        order = await self.order_repository.get_order(order_id=order_id, db=db)

        if not order:
            return None

        return OrderModel(**dict(order))

    async def get_user_orders(self, user_id: int, db: asyncpg.Connection) -> list[OrderModel]:
        order_models = []

        orders = await self.order_repository.get_user_orders(user_id=user_id, db=db)

        for order in orders:
            order_model = OrderModel(**dict(order))
            order_models.append(order_model)

        return order_models

    async def get_order_items(self, order_id: int, db: asyncpg.Connection) -> list[ItemModel]:
        order_items = await self.order_repository.get_order_items(order_id=order_id, db=db)
        order_item_models = []

        for order_item in order_items:
            order_item_model = ItemModel(**dict(order_item))
            order_item_models.append(order_item_model)

        return order_item_models

    async def get_order_summary(self, order_id: int, db: asyncpg.Connection) -> OrderSummaryModel:
        order_model = await self.get_order(order_id=order_id, db=db)
        item_models = await self.get_order_items(order_id=order_id, db=db)
        return OrderSummaryModel(item_models=item_models, order_model=order_model)  # type: ignore

    async def get_user_orders_summary(self, user_id: int, db: asyncpg.Connection) -> list[OrderSummaryModel]:
        order_summary_models = []

        order_models = await self.get_user_orders(user_id=user_id, db=db)

        for order_model in order_models:
            order_summary_model = await self.get_order_summary(order_id=order_model.id, db=db)
            order_summary_models.append(order_summary_model)

        return order_summary_models
