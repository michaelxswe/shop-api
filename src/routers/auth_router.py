import asyncpg
from config.settings import Settings
from fastapi import APIRouter, Depends, HTTPException, status
from models import AccessTokenModel, UserCredentialModel
from redis import Redis
from services.auth_service import AuthService
from services.user_service import UserService
from states import get_access_token, get_postgres_conn, get_redis, get_settings

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post(
    path="/sign-in",
    status_code=status.HTTP_200_OK,
    response_model=AccessTokenModel,
    summary="Sign in to retrieve access token",
)
async def sign_in(
    user_credential_model: UserCredentialModel,
    user_service: UserService = Depends(),
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
    db: asyncpg.Connection = Depends(get_postgres_conn),
):
    user_model = await user_service.verify_user(
        username=user_credential_model.username, password=user_credential_model.password, db=db
    )

    if not user_model:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid sign-in credentials")

    access_token_model = auth_service.create_access_token(
        user_id=user_model.id, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return access_token_model


@router.post(
    path="/sign-out",
    status_code=status.HTTP_200_OK,
    response_model=None,
    summary="Sign out invokes current access token",
)
async def sign_out(
    access_token: str = Depends(get_access_token),
    auth_service: AuthService = Depends(),
    settings: Settings = Depends(get_settings),
    redis: Redis = Depends(get_redis),
):
    claims = auth_service.validate_access_token(
        access_token=access_token, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM, redis=redis
    )

    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    tid = claims["tid"]
    auth_service.invoke_access_token(tid=tid, redis=redis)
