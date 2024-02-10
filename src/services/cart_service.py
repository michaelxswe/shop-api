import asyncpg
from fastapi import Depends
from models import CartSummaryModel, ItemModel
from repositories.cart_repository import CartRepository


class CartService:
    def __init__(self, cart_repository: CartRepository = Depends()):
        self.cart_repository = cart_repository

    async def add_item(self, item_id: int, qty: int, user_id: int, db: asyncpg.Connection) -> None:
        item = await self.cart_repository.get_item(item_id=item_id, user_id=user_id, db=db)

        if not item:
            await self.cart_repository.add_item(item_id=item_id, qty=qty, user_id=user_id, db=db)
        else:
            await self.cart_repository.increase_qty(item_id=item_id, qty=qty, user_id=user_id, db=db)

    async def remove_item(self, item_id: int, qty: int, user_id: int, db: asyncpg.Connection) -> bool:
        item = await self.cart_repository.get_item(item_id=item_id, user_id=user_id, db=db)

        if not item:
            return False

        await self.cart_repository.decrease_qty(item_id=item_id, qty=qty, user_id=user_id, db=db)
        await self.cart_repository.clean_up(item_id=item_id, user_id=user_id, db=db)
        return True

    async def clear_cart(self, user_id: int, db: asyncpg.Connection) -> None:
        await self.cart_repository.clear_cart(user_id=user_id, db=db)

    async def get_items(self, user_id: int, db: asyncpg.Connection) -> list[ItemModel]:
        cart = await self.cart_repository.get_cart(user_id=user_id, db=db)
        item_models = []
        for item in cart:
            item_model = ItemModel(**dict(item))
            item_models.append(item_model)

        return item_models

    async def get_total(self, user_id: int, db: asyncpg.Connection) -> float:
        total = await self.cart_repository.get_total(user_id=user_id, db=db)

        if not total:
            return 0

        return total["total"]

    async def get_cart_summary(self, user_id: int, db: asyncpg.Connection) -> CartSummaryModel:
        total = await self.get_total(user_id=user_id, db=db)
        item_models = await self.get_items(user_id=user_id, db=db)
        return CartSummaryModel(item_models=item_models, total=total)
