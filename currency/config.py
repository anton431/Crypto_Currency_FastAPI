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
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        path=f"/{os.getenv('POSTGRES_DB') or ''}",
    )
    SECRET_KEY = os.getenv("SECRET_KEY")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
currencies = ["BTC", "ETH"]