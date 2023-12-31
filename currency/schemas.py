from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: int
    username: str
    budget: int | None = None

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True


class UserUpdate(UserCreate):
    pass


class Currency(BaseModel):
    name: str
    price: float
    time: datetime

    class Config:
        orm_mode = True
