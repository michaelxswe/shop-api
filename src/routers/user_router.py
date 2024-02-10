import asyncpg
from config.settings import Settings
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    UserCredentialModel,
    UserModel,
    UserPasswordModel,
    UserPasswordResetModel,
)
from redis import Redis
from services.auth_service import AuthService
from services.user_service import UserService
from states import get_access_token, get_postgres_conn, get_redis, get_settings

router = APIRouter(prefix="/v1/users", tags=["User"])


@router.post(path="", status_code=status.HTTP_201_CREATED, response_model=UserModel, summary="Register user")
async def register_user(
    user_credential_model: UserCredentialModel,
    user_service: UserService = Depends(),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    async with db.transaction():
        user_model = await user_service.register_user(
            username=user_credential_model.username, password=user_credential_model.password, db=db
        )
    return user_model


@router.get(path="/me", status_code=200, response_model=UserModel, summary="Get my info")
async def get_user(
    access_token: str = Depends(get_access_token),
    user_service: UserService = Depends(),
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
    redis: Redis = Depends(get_redis),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    user_id = claims["sub"]
    user_model = await user_service.get_user(user_id=user_id, db=db)
    return user_model


@router.patch(
    path="/me/password",
    status_code=status.HTTP_200_OK,
    response_model=None,
    summary="Reset my password",
)
async def reset_password(
    user_password_reset_model: UserPasswordResetModel = Depends(),
    access_token: str = Depends(get_access_token),
    user_service: UserService = Depends(),
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
    db: asyncpg.Connection = Depends(get_postgres_conn),
    redis: Redis = Depends(get_redis),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    user_id = claims["sub"]

    async with db.transaction():
        res = await user_service.verify_password(user_id=user_id, password=user_password_reset_model.password, db=db)

        if not res:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")

        await user_service.reset_password(new_password=user_password_reset_model.new_password, user_id=user_id, db=db)
        auth_service.set_access_token_min_issue_date(user_id=user_id, redis=redis)


@router.delete(path="/me", status_code=status.HTTP_200_OK, response_model=None, summary="Delete my accoun")
async def delete_user(
    user_password_model: UserPasswordModel,
    access_token: str = Depends(get_access_token),
    user_service: UserService = Depends(),
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
    db: asyncpg.Connection = Depends(get_postgres_conn),
    redis: Redis = Depends(get_redis),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    user_id = claims["sub"]

    async with db.transaction():
        if not await user_service.verify_password(user_id=user_id, password=user_password_model.password, db=db):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")

        await user_service.delete_user(user_id=user_id, db=db)
        auth_service.set_access_token_min_issue_date(user_id=user_id, redis=redis)
