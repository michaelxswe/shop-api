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


class ShippingDetailModel(BaseModel):
    id: int
    address: str


class ShippingDetailRegistrationModel(BaseModel):
    address: str


class PaymentDetailModel(BaseModel):
    id: int
    card_number: str
    cvv: str


class PaymentDetailRegistrationModel(BaseModel):
    card_number: str
    cvv: str


class OrderRegistrationModel(BaseModel):
    shipping_detail_registration_model: ShippingDetailRegistrationModel
    payment_detail_registration_model: PaymentDetailRegistrationModel


class OrderModel(BaseModel):
    id: int
    total: float
    user_id: int
    shipping_detail_id: int
    payment_detail_id: int
    order_date: datetime


class OrderDetailModel(BaseModel):
    item_id: int
    qty: int
    order_id: int


class OrderSummaryModel(BaseModel):
    item_models: list[ItemModel]
    order_model: OrderModel


class ItemRatingModel(BaseModel):
    item_id: int
    rating: int
