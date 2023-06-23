import asyncio
import json
import logging
import random
import sys
import time
from datetime import datetime
from typing import Iterator

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from models import CurrencyDB

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# random.seed()  # Initialize the random number generator





async def generate_BTC_data(request: Request, session: AsyncSession) -> Iterator[str]:
    """
    Generates random value between 0 and 100
    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    client_ip = request.client.host
    currencies = await session.execute(select(CurrencyDB).where(CurrencyDB.name == "BTC"))
    currencies = currencies.scalars().all()
    logger.info("Client %s connected", client_ip)
    for currency in currencies:
        json_data = json.dumps(
            {
                "time": currency.time,
                "value": currency.price,
            }
        )
        yield f"data:{json_data}\n\n"
        await asyncio.sleep(1)

