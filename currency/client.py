import json
from datetime import datetime

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CurrencyDB
from schemas import Currency


def take_msg(currency):
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "public/ticker",
        "params": {
            "instrument_name": f"{currency}-PERPETUAL"
        }
    }
    return json.dumps(msg)


async def get_tickers(currency: str,
                      db: AsyncSession):

    async with aiohttp.ClientSession() as session:
        async with session.post('https://test.deribit.com/api/v2',
                                data=take_msg(currency)) as resp:
            ticker = await resp.json()

            name: str = ticker.get("result").get("instrument_name").split('-')[0]
            price: float = ticker.get('result').get('index_price')
            timestamp: int = ticker.get('result').get('timestamp')//1000

            time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            new_ticker = CurrencyDB(name=name, price=price, time=time)

            db.add(new_ticker)

            return Currency(name=name, price=price, time=time)

async def get_currencies(session: AsyncSession):
    currencies = await session.execute(select(CurrencyDB))
    return currencies.scalars().all()



