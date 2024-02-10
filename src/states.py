import asyncpg
import redis
from config.settings import Settings
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

create_all_tables_query = """
    create table users(
        id serial primary key,
        username varchar(50) unique,
        password varchar(50) not null
    );

    create table items(
        id serial primary key,
        name varchar(25) unique,
        price numeric(10, 2) not null,
        category varchar(25) not null,
        qty integer not null
    );

    create table payment_details(
        id serial primary key,
        card_number varchar(25) not null,
        cvv varchar(25) not null
    );

    create table shipping_details(
        id serial primary key,
        address varchar(100) not null
    );

    create table orders(
        id serial primary key,
        total numeric(10, 2) not null,
        user_id integer references users(id) on delete cascade not null,
        shipping_detail_id integer references shipping_details(id) on delete set null,
        payment_detail_id integer references payment_details(id) on delete set null,
        order_date timestamptz default current_timestamp not null
    );

    create table order_details(
        item_id integer references items(id) on delete set null,
        qty integer not null,
        order_id integer references orders(id) on delete cascade,
        primary key(item_id, order_id)
    );

    create table carts(
        item_id integer references items(id) on delete cascade,
        qty integer not null,
        user_id integer references users(id) on delete cascade,
        primary key(item_id, user_id)
    );

    create table item_ratings(
        item_id integer references items(id) on delete cascade,
        rating integer check(rating between 1 and 5) not null
    );

"""

class PostgresClient:
    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def create_all_tables(self):
        async with self.pool.acquire() as conn:  # type: ignore
            await conn.execute(create_all_tables_query)

    async def setup(self):
        self.pool = await asyncpg.create_pool(self.url)
        await self.create_all_tables()

    async def teardown(self):
        await self.pool.close()  # type: ignore


class RedisClient:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.pool = None
        self.redis = None

    def setup(self):
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
        )
        self.redis = redis.Redis(connection_pool=self.pool)
        self.redis.flushdb()

    def teardown(self):
        self.redis.flushdb()  # type: ignore
        self.pool.disconnect()  # type: ignore


http_bearer = HTTPBearer()


def get_access_token(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    access_token = credentials.credentials
    return access_token


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_postgres_client(request: Request) -> PostgresClient:
    return request.app.state.postgres_client


async def get_postgres_conn(postgres_client: PostgresClient = Depends(get_postgres_client)):
    async with postgres_client.pool.acquire() as conn:  # type: ignore
        yield conn


async def get_redis_client(request: Request) -> RedisClient:
    return request.app.state.redis_client


async def get_redis(redis_client: RedisClient = Depends(get_redis_client)) -> redis.Redis:
    return redis_client.redis  # type: ignore
