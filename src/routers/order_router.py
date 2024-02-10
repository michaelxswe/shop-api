import asyncpg
from config.settings import Settings
from fastapi import APIRouter, Depends, HTTPException, status
from models import OrderRegistrationModel, OrderSummaryModel
from redis import Redis
from services.auth_service import AuthService
from services.cart_service import CartService
from services.item_service import ItemService
from services.order_service import OrderService
from states import get_access_token, get_postgres_conn, get_redis, get_settings

router = APIRouter(prefix="/v1/orders", tags=["Order"])


@router.get("/me", response_model=list[OrderSummaryModel], summary="Get my order history")
async def get_user_orders(
    order_service: OrderService = Depends(),
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
    user_orders_summary_model = await order_service.get_user_orders_summary(user_id=user_id, db=db)
    return user_orders_summary_model


@router.post(path="/me", status_code=status.HTTP_200_OK, response_model=OrderSummaryModel, summary="Submit my order")
async def order(
    order_registration_model: OrderRegistrationModel,
    order_service: OrderService = Depends(),
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your cart is empty.")

    async with db.transaction():
        shipping_detail_model = await order_service.register_shipping_detail(
            address=order_registration_model.shipping_detail_registration_model.address, db=db
        )

        payment_detail_model = await order_service.register_payment_detail(
            card_number=order_registration_model.payment_detail_registration_model.card_number,
            cvv=order_registration_model.payment_detail_registration_model.cvv,
            db=db,
        )

        total = await cart_service.get_total(user_id=user_id, db=db)

        order_model = await order_service.register_order(
            total=total,
            user_id=user_id,
            shipping_detail_id=shipping_detail_model.id,
            payment_detail_id=payment_detail_model.id,
            db=db,
        )

        for item_model in item_models:
            qty = await item_service.get_qty(item_id=item_model.id, db=db)
            if item_model.qty > qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{item_model.name} is low in stock, only {qty} left.",
                )

            await item_service.decrease_qty(item_id=item_model.id, qty=item_model.qty, db=db)
            await order_service.register_order_detail(
                item_id=item_model.id, qty=item_model.qty, order_id=order_model.id, db=db
            )

        await cart_service.clear_cart(user_id=user_id, db=db)
        order_summary_model = await order_service.get_order_summary(order_id=order_model.id, db=db)
        return order_summary_model
