import asyncpg
from config.settings import Settings
from fastapi import APIRouter, Depends, HTTPException, status
from models import DetailedReceiptModel, PurchaseRegistrationModel
from redis import Redis
from services.auth_service import AuthService
from services.cart_service import CartService
from services.item_service import ItemService
from services.purchase_service import PurchaseService
from states import get_access_token, get_postgres_conn, get_redis, get_settings

router = APIRouter(prefix="/v1/purchases", tags=["Purchase"])


@router.get("/receipts/me", response_model=list[DetailedReceiptModel], summary="Get purchase history")
async def get_user_receipts(
    purchase_service: PurchaseService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
    settings: Settings = Depends(get_settings),
    redis: Redis = Depends(get_redis),
    auth_service: AuthService = Depends(),
    access_token: str = Depends(get_access_token),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    user_id = claims["sub"]
    detailed_user_receipt_models = await purchase_service.get_detialed_user_receipts(user_id=user_id, db=db)
    return detailed_user_receipt_models


@router.post(path="", status_code=status.HTTP_200_OK, response_model=DetailedReceiptModel, summary="Submit purchase")
async def purchase(
    purchase_registration_model: PurchaseRegistrationModel,
    purchase_service: PurchaseService = Depends(),
    cart_service: CartService = Depends(),
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
    settings: Settings = Depends(get_settings),
    redis: Redis = Depends(get_redis),
    auth_service: AuthService = Depends(),
    access_token: str = Depends(get_access_token),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    user_id = claims["sub"]

    item_models = await cart_service.get_items(user_id=user_id, db=db)

    if len(item_models) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty Cart.")

    async with db.transaction():
        shipping_model = await purchase_service.register_shipping(
            address=purchase_registration_model.shipping_registration_model.address, db=db
        )

        payment_model = await purchase_service.register_payment(
            card_number=purchase_registration_model.payment_registration_model.card_number,
            cvv=purchase_registration_model.payment_registration_model.cvv,
            db=db,
        )

        total = await cart_service.get_total(user_id=user_id, db=db)

        receipt_model = await purchase_service.register_receipt(
            total=total, user_id=user_id, shipping_id=shipping_model.id, payment_id=payment_model.id, db=db
        )

        for item_model in item_models:
            qty = await item_service.get_qty(item_id=item_model.id, db=db)
            if item_model.qty > qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{item_model.name} is low in stock, only {qty} left.",
                )

            await item_service.decrease_qty(item_id=item_model.id, qty=item_model.qty, db=db)
            await purchase_service.register_purchase(
                item_id=item_model.id, qty=item_model.qty, receipt_id=receipt_model.id, db=db
            )

        await cart_service.clear_cart(user_id=user_id, db=db)
        user_receipt_model = await purchase_service.get_detailed_receipt(receipt_id=receipt_model.id, db=db)
        return user_receipt_model
