import time

import asyncpg
import jwt
from config.settings import Settings
from fastapi import FastAPI, Request, status
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routers import auth_router, cart_router, item_router, order_router, user_router
from states import PostgresClient, RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up application")
    app.state.settings = Settings()  # type: ignore
    app.state.postgres_client = PostgresClient(app.state.settings.POSTGRES_URL)
    app.state.redis_client = RedisClient(
        app.state.settings.REDIS_HOST, app.state.settings.REDIS_PORT, app.state.settings.REDIS_PWD
    )

    await app.state.postgres_client.setup()
    app.state.redis_client.setup()
    yield
    await app.state.postgres_client.teardown()
    app.state.redis_client.teardown()
    print("Shutting down applicaiton")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


@app.exception_handler(jwt.PyJWTError)
async def jwt_exception_handler(request: Request, exc: jwt.PyJWTError):
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})


@app.exception_handler(asyncpg.PostgresError)
async def postgrss_exception_handler(request: Request, exc: asyncpg.PostgresError):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})


@app.middleware("http")
async def response_time_tracker(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    end = time.time()
    response_time = (end - start) * 1000  # Convert seconds to milliseconds
    print(f"Response time: {response_time} ms")
    return response


app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(item_router.router)
app.include_router(cart_router.router)
app.include_router(order_router.router)


@app.get("/ping", tags=["Health"], summary="Check server is running")
async def ping():
    return {"response": "pong"}
