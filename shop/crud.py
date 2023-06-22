from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timedelta
from typing import Annotated, Union, Any, Sequence

from sqlalchemy import select
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

import models
from database import get_session
from models import *
from schemas import CitySchema, TokenData, UserCreate
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_biggest_cities(session: AsyncSession):
    cities = await session.execute(select(CityDB).order_by(CityDB.population.desc()).limit(5))
    return cities.scalars().all()


def add_city(session: AsyncSession, city: CitySchema):
    new_city = CityDB(name=city.name, population=city.population)
    session.add(new_city)
    return new_city


def verify_password(plain_password, hashed_password):
    """
    Check whether the received password matches the saved hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    """
    Hash the password coming from the user.
    """
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str):
    """
    Get the current user.
    """
    user = await session.execute(select(UserDB).where(
        models.UserDB.username == username))
    print("Attention")
    print(user)
    if user:
        return user.scalars().first()


async def create_user(session: AsyncSession, user: UserCreate):
    """
    Create a new user by name and password.
    """
    print("Fake_hashed")
    fake_hashed_password = await get_password_hash(user.password)
    print("Create user")
    db_user = models.UserDB(username=user.username,
                            hashed_password=fake_hashed_password,
                            salary=40000)
    session.add(db_user)
    print("Commit")
    await session.commit()
    await session.refresh(db_user)

    return db_user


async def authenticate_user(session: AsyncSession, username: str, password: str):
    """
    Authenticate and return the user.
    """
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None):
    """
    Creating a token with an expiration time of 5 minutes.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_session)):
    """
    Get the JWT tokens, Decrypt the received token, verify it,
    and return the current user. If the token is invalid, return
    an HTTP error immediately.
    """
    print("credentials_exception")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(session=session, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user
