import asyncpg
from fastapi import Depends
from models import ItemModel, ItemRatingModel
from repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, item_repository: ItemRepository = Depends()):
        self.item_repository = item_repository

    async def register_item(
        self, name: str, price: float, category: str, qty: int, db: asyncpg.Connection
    ) -> ItemModel:
        item = await self.item_repository.register_item(name=name, price=price, category=category, qty=qty, db=db)
        return ItemModel(**dict(item))  # type: ignore

    async def get_item(self, item_id: int, db: asyncpg.Connection) -> ItemModel | None:
        item = await self.item_repository.get_item(item_id=item_id, db=db)

        if not item:
            return None

        return ItemModel(**dict(item))

    async def get_qty(self, item_id: int, db: asyncpg.Connection) -> int:
        item_model = await self.get_item(item_id=item_id, db=db)

        if not item_model:
            return 0

        return item_model.qty

    async def remove_item(self, item_id: int, db: asyncpg.Connection) -> None:
        await self.item_repository.remove_item(item_id=item_id, db=db)

    async def get_all_items(self, db: asyncpg.Connection) -> list[ItemModel]:
        items = await self.item_repository.get_all_items(db=db)
        item_models = []

        for item in items:
            item_model = ItemModel(**dict(item))
            item_models.append(item_model)

        return item_models

    async def get_items_by_category(self, category: str, db: asyncpg.Connection) -> list[ItemModel]:
        items = await self.item_repository.get_items_by_category(category=category, db=db)
        item_models = []

        for item in items:
            item_model = ItemModel(**dict(item))
            item_models.append(item_model)
        return item_models

    async def decrease_qty(self, item_id: int, qty: int, db: asyncpg.Connection) -> None:
        await self.item_repository.decrease_qty(item_id=item_id, qty=qty, db=db)

    async def increase_qty(self, item_id: int, qty: int, db: asyncpg.Connection) -> None:
        await self.item_repository.increase_qty(item_id=item_id, qty=qty, db=db)

    async def register_item_rating(self, item_id: int, rating: int, db: asyncpg.Connection) -> None:
        await self.item_repository.register_item_rating(item_id=item_id, rating=rating, db=db)

    async def get_item_ratings(self, item_id: int, db: asyncpg.Connection) -> list[ItemRatingModel]:
        item_rating_models = []

        item_ratings = await self.item_repository.get_item_ratings(item_id=item_id, db=db)
        for item_rating in item_ratings:
            item_rating_model = ItemRatingModel(**dict(item_rating))
            item_rating_models.append(item_rating_model)

        return item_rating_models
