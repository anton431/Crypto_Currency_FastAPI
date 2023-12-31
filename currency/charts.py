import asyncio
import json
from typing import Iterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CurrencyDB

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
                "time": f"{currency.time}",
                "value": currency.price,
            }
        )
        yield f"data:{json_data}\n\n"
        await asyncio.sleep(1)
