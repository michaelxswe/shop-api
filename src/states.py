import asyncpg
import redis
from config.settings import Settings
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

create_all_tables_query = """
    drop schema if exists public cascade;
    create schema public;

    create table users(
        id serial primary key,
        username varchar(50) unique,
        password varchar(50) not null
    );

    create table items(
        id serial primary key,
        name varchar(25) unique,
        price numeric(10, 2) not null,
        category varchar(25) check(category in ('Action', 'Adventure', 'Puzzle', 'Strategy')),
        qty integer not null
    );

    create table payments(
        id serial primary key,
        card_number varchar(25) not null,
        cvv varchar(25) not null
    );

    create table shippings(
        id serial primary key,
        address varchar(100) not null
    );

    create table receipts(
        id serial primary key,
        total numeric(10, 2) not null,
        user_id integer references users(id) on delete cascade not null,
        shipping_id integer references shippings(id) on delete set null,
        payment_id integer references payments(id) on delete set null,
        date_created timestamptz default current_timestamp not null
    );

    create table purchases(
        id serial primary key,
        item_id integer references items(id) on delete set null,
        qty integer not null,
        receipt_id integer references receipts(id) on delete cascade
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

test_data = """
    insert into users(username, password) values ('string', 'string');

    insert into items(name, price, category, qty) values
    ('gta5', 30, 'Action', 200),
    ('gta4', 20, 'Action', 250),
    ('HearthStone', 0, 'Strategy', 500);
"""

drop_all_tables_query = """
    drop schema if exists public cascade;
    create schema public;
"""


class PostgresClient:
    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def create_all_tables(self):
        async with self.pool.acquire() as conn:  # type: ignore
            await conn.execute(create_all_tables_query)
            await conn.execute(test_data)

    async def drop_all_tables(self):
        async with self.pool.acquire() as conn:  # type: ignore
            await conn.execute(drop_all_tables_query)

    async def setup(self):
        self.pool = await asyncpg.create_pool(self.url)
        await self.create_all_tables()

    async def teardown(self):
        await self.drop_all_tables()
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
