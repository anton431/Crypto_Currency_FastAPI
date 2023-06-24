import asyncio
import json
from typing import Iterator

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CurrencyDB


app = FastAPI()
templates = Jinja2Templates(directory="templates")

BTC = "BTC"

async def generate_BTC_data(session: AsyncSession) -> Iterator[str]:
    """
    Generates data for the BTC chart
    """
    currencies = await session.execute(select(CurrencyDB).
                                       where(CurrencyDB.name == BTC))
    currencies = currencies.scalars().all()
    for currency in currencies:
        json_data = json.dumps(
            {
                "time": currency.time,
                "value": currency.price,
            }
        )
        yield f"data:{json_data}\n\n"
        await asyncio.sleep(1)

