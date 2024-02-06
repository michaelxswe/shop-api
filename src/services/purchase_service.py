import asyncpg
from databases.purchase_database import PurchaseDatabase
from fastapi import Depends
from models import (
    DetailedReceiptModel,
    ItemModel,
    PaymentModel,
    PurchaseModel,
    ReceiptModel,
    ShippingModel,
)


class PurchaseService:
    def __init__(self, purchase_database: PurchaseDatabase = Depends()):
        self.purchase_database = purchase_database

    async def register_shipping(self, address: str, db: asyncpg.Connection) -> ShippingModel:
        shipping = await self.purchase_database.register_shipping(address=address, db=db)
        return ShippingModel(**dict(shipping))

    async def register_payment(self, card_number: str, cvv: str, db: asyncpg.Connection) -> PaymentModel:
        payment = await self.purchase_database.register_payment(card_number=card_number, cvv=cvv, db=db)
        return PaymentModel(**dict(payment))

    async def register_receipt(
        self, total: float, user_id: int, shipping_id: int, payment_id: int, db: asyncpg.Connection
    ) -> ReceiptModel:
        receipt = await self.purchase_database.register_receipt(
            total=total, user_id=user_id, shipping_id=shipping_id, payment_id=payment_id, db=db
        )
        return ReceiptModel(**dict(receipt))

    async def register_purchase(self, item_id: int, qty: int, receipt_id: int, db: asyncpg.Connection) -> PurchaseModel:
        purchase = await self.purchase_database.register_purchase(
            item_id=item_id, qty=qty, receipt_id=receipt_id, db=db
        )
        return PurchaseModel(**dict(purchase))

    async def get_receipt(self, receipt_id: int, db: asyncpg.Connection) -> ReceiptModel | None:
        receipt = await self.purchase_database.get_receipt(receipt_id=receipt_id, db=db)

        if not receipt:
            return None
        
        return ReceiptModel(**dict(receipt))

    async def get_user_receipts(self, user_id: int, db: asyncpg.Connection) -> list[ReceiptModel]:
        receipt_models = []

        receipts = await self.purchase_database.get_user_receipts(user_id=user_id, db=db)

        for receipt in receipts:
            receipt_model = ReceiptModel(**dict(receipt))
            receipt_models.append(receipt_model)

        return receipt_models

    async def get_purchased_items_by_receipt(self, receipt_id: int, db: asyncpg.Connection) -> list[ItemModel]:
        items = await self.purchase_database.get_purchased_items_by_receipt(receipt_id=receipt_id, db=db)
        item_models = []

        for item in items:
            item_model = ItemModel(**dict(item))
            item_models.append(item_model)
            
        return item_models

    async def get_detailed_receipt(self, receipt_id: int, db: asyncpg.Connection) -> DetailedReceiptModel:
        receipt_model = await self.get_receipt(receipt_id=receipt_id, db=db)
        item_models = await self.get_purchased_items_by_receipt(receipt_id=receipt_id, db=db)
        return DetailedReceiptModel(item_models=item_models, receipt_model=receipt_model) # type: ignore

    async def get_detialed_user_receipts(self, user_id: int, db: asyncpg.Connection) -> list[DetailedReceiptModel]:
        detailed_receipt_models = []
        receipt_models = await self.get_user_receipts(user_id=user_id, db=db)

        for receipt_model in receipt_models:
            detailed_receipt_model = await self.get_detailed_receipt(receipt_id=receipt_model.id, db=db)
            detailed_receipt_models.append(detailed_receipt_model)
            
        return detailed_receipt_models
