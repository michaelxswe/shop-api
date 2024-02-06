from datetime import datetime

from pydantic import BaseModel


class AccessTokenModel(BaseModel):
    type: str
    value: str


class UserModel(BaseModel):
    id: int
    username: str
    password: str


class UserCredentialModel(BaseModel):
    username: str
    password: str


class UserPasswordResetModel(BaseModel):
    password: str
    new_password: str


class UserPasswordModel(BaseModel):
    password: str


class ItemModel(BaseModel):
    id: int
    name: str
    price: float
    category: str
    qty: int


class ItemRegistrationModel(BaseModel):
    name: str
    price: float
    category: str
    qty: int


class CartSummaryModel(BaseModel):
    item_models: list[ItemModel]
    total: float


class ShippingModel(BaseModel):
    id: int
    address: str


class ShippingRegistrationModel(BaseModel):
    address: str


class PaymentModel(BaseModel):
    id: int
    card_number: str
    cvv: str


class PaymentRegistrationModel(BaseModel):
    card_number: str
    cvv: str


class PurchaseRegistrationModel(BaseModel):
    shipping_registration_model: ShippingRegistrationModel
    payment_registration_model: PaymentRegistrationModel


class ReceiptModel(BaseModel):
    id: int
    total: float
    user_id: int
    shipping_id: int
    payment_id: int
    date_created: datetime


class PurchaseModel(BaseModel):
    id: int
    item_id: int
    qty: int
    receipt_id: int


class DetailedReceiptModel(BaseModel):
    item_models: list[ItemModel]
    receipt_model: ReceiptModel

class ItemRatingModel(BaseModel):
    item_id: int
    rating: int


