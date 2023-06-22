# This is a sample Python script.
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud import get_password_hash
from database import get_session
from models import UserDB
from schemas import UserCreate


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


async def get_user(username: str,session: AsyncSession = Depends(get_session)):
    """
    Get the current user.
    """
    user = await session.execute(select(UserDB).where(
        UserDB.username == username))
    print(user.scalars().all())

get_user(username="Anton", session=Depends(get_session))