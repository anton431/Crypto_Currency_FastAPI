from datetime import datetime, timedelta
from typing import Annotated, Union

from sqlalchemy import select
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

import schemas
import models
import database
import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """
    Check whether the received password matches the saved hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password) -> str:
    """
    Hash the password coming from the user.
    """
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str) -> schemas.UserInDB:
    """
    Get the current user.
    """
    user = await session.execute(select(models.UserDB).where(
        models.UserDB.username == username))
    if user:
        return user.scalars().first()


async def create_user(session: AsyncSession, user: schemas.UserCreate) -> models.UserDB:
    """
    Create a new user by name and password.
    """
    fake_hashed_password = await get_password_hash(user.password)
    db_user = models.UserDB(username=user.username,
                            hashed_password=fake_hashed_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


async def authenticate_user(session: AsyncSession, username: str,
                            password: str) -> bool | schemas.UserInDB:
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
                        expires_delta: Union[timedelta, None] = None) -> str:
    """
    Creating a token with an expiration time of 5 minutes.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY,
                             algorithm=config.ALGORITHM)

    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(database.get_session)) -> schemas.UserInDB:
    """
    Get the JWT tokens, Decrypt the received token, verify it,
    and return the current user. If the token is invalid, return
    an HTTP error immediately.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY,
                             algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(session=session, username=token_data.username)
    if user is None:
        raise credentials_exception

    return await user
