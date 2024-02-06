import asyncpg
from config.settings import Settings
from fastapi import APIRouter, Depends, HTTPException, status
from models import CartSummaryModel
from redis import Redis
from services.auth_service import AuthService
from services.cart_service import CartService
from services.item_service import ItemService
from states import get_access_token, get_postgres_conn, get_redis, get_settings

router = APIRouter(prefix="/v1/carts", tags=["Cart"])


@router.patch(
    path="/{item_id}", status_code=status.HTTP_200_OK, response_model=None, summary="Add or remove items to cart"
)
async def update_item_qty(
    item_id: int,
    qty: int,
    access_token: str = Depends(get_access_token),
    cart_service: CartService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
    item_service: ItemService = Depends(),
    settings: Settings = Depends(get_settings),
    redis: Redis = Depends(get_redis),
    auth_service: AuthService = Depends(),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    user_id = claims["sub"]

    item_model = await item_service.get_item(item_id=item_id, db=db)

    if not item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")

    async with db.transaction():
        if qty == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity can't be 0.")

        elif qty > 0:
            await cart_service.add_item(item_id=item_id, qty=qty, user_id=user_id, db=db)

        else:
            res = await cart_service.remove_item(item_id=item_id, qty=abs(qty), user_id=user_id, db=db)

            if not res:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in your cart.")


@router.delete(path="", status_code=status.HTTP_200_OK, response_model=None, summary="Remove all items from cart.")
async def clear_cart(
    cart_service: CartService = Depends(),
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

    async with db.transaction():
        await cart_service.clear_cart(user_id=user_id, db=db)


@router.get(path="/me", status_code=status.HTTP_200_OK, response_model=CartSummaryModel, summary="Show my cart")
async def get_cart_summary(
    cart_service: CartService = Depends(),
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
    cart_summary_model = await cart_service.get_cart_summary(user_id=user_id, db=db)
    return cart_summary_model
