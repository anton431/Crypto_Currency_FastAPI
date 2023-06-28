import os

from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_SERVER"),
        port=os.getenv("POSTGRES_PORT"),
        path=f"/{os.getenv('POSTGRES_DB')}",
    )
    test_asyncpg_url: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=os.getenv("POSTGRES_USER_TEST"),
        password=os.getenv("POSTGRES_PASSWORD_TEST"),
        host=os.getenv("POSTGRES_SERVER_TEST"),
        port=os.getenv("POSTGRES_PORT_TEST"),
        path=f"/{os.getenv('POSTGRES_DB_TEST')}",
    )
    SECRET_KEY = os.getenv("SECRET_KEY")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
currencies = ["BTC", "ETH"]