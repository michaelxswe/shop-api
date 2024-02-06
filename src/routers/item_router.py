import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from models import ItemModel, ItemRatingModel, ItemRegistrationModel
from services.item_service import ItemService
from states import get_postgres_conn

router = APIRouter(prefix="/v1/items", tags=["Item"])


@router.post(path="", status_code=status.HTTP_201_CREATED, response_model=ItemModel, summary="Register item")
async def register_item(
    item_registration_model: ItemRegistrationModel,
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    async with db.transaction():
        item_model = await item_service.register_item(
            name=item_registration_model.name,
            price=item_registration_model.price,
            category=item_registration_model.category,
            qty=item_registration_model.qty,
            db=db,
        )
    return item_model


@router.get(path="/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemModel, summary="Search item")
async def get_item(
    item_id: int,
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    item_model = await item_service.get_item(item_id=item_id, db=db)

    if not item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found.")

    return item_model


@router.delete(path="/{item_id}", status_code=status.HTTP_200_OK, response_model=None, summary="Remove item")
async def remove_item(
    item_id: int,
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    item_model = await item_service.get_item(item_id=item_id, db=db)

    if not item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found.")

    await item_service.remove_item(item_id=item_id, db=db)


@router.get(path="", status_code=status.HTTP_200_OK, response_model=list[ItemModel], summary="Get all items")
async def get_all_items(
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    item_models = await item_service.get_all_items(db=db)
    return item_models


@router.patch(path="/{item_id}", status_code=status.HTTP_200_OK, response_model=None, summary="Update item quantity")
async def update_item_qty(
    item_id: int, qty: int, item_service: ItemService = Depends(), db: asyncpg.Connection = Depends(get_postgres_conn)
):
    item_model = await item_service.get_item(item_id=item_id, db=db)

    if not item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found.")

    async with db.transaction():
        if qty == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity can't be 0.")
        elif qty > 0:
            await item_service.increase_qty(item_id=item_id, qty=qty, db=db)
        else:
            await item_service.decrease_qty(item_id=item_id, qty=abs(qty), db=db)


@router.get(
    path="/category/{category}",
    status_code=status.HTTP_200_OK,
    response_model=list[ItemModel],
    summary="Search items by category",
)
async def get_items_by_category(
    category: str,
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    items = await item_service.get_items_by_category(category=category, db=db)
    return items


@router.post(path="/ratings", status_code=status.HTTP_200_OK, response_model=None, summary="Rate an item")
async def rate_item(
    item_rating_model: ItemRatingModel,
    item_service: ItemService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    if item_rating_model.rating < 1 or item_rating_model.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be in between 1 and 5")

    item_model = await item_service.get_item(item_id=item_rating_model.item_id, db=db)

    if not item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found.")

    await item_service.register_item_rating(item_id=item_rating_model.item_id, rating=item_rating_model.rating, db=db)


@router.get(
    path="/{item_id}/ratings",
    status_code=status.HTTP_200_OK,
    response_model=list[ItemRatingModel],
    summary="Get all ratings of this item",
)
async def get_item_ratings(
    item_id: int, item_service: ItemService = Depends(), db: asyncpg.Connection = Depends(get_postgres_conn)
):
    item_rating_models = await item_service.get_item_ratings(item_id=item_id, db=db)
    return item_rating_models
