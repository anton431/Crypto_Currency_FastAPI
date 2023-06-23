import json
from datetime import datetime

import aiohttp
import asyncio

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import CurrencyDB

currencies = ["BTC", "ETH"]


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
                    current_user_id,
                      db: AsyncSession):

    async with aiohttp.ClientSession() as session:
        async with session.post('https://test.deribit.com/api/v2',
                                data=take_msg(currency)) as resp:
            ticker = await resp.json()

            name: str = ticker.get("result").get("instrument_name").split('-')[0]
            price: float = ticker.get('result').get('index_price')
            timestamp: int = ticker.get('result').get('timestamp')//1000
            print(timestamp, type(timestamp))
            time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            new_ticker = CurrencyDB(name=name, price=price, time=time, user_id=current_user_id)
            print(new_ticker.time)
            print(new_ticker)
            db.add(new_ticker)
            await db.commit()
            await db.refresh(new_ticker)

            return new_ticker

# sessionDB: AsyncSession = Depends(get_session)
# asyncio.run(get_tickers("BTC", sessionDB))


