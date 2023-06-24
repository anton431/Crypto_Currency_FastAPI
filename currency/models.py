from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CurrencyDB(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[float]
    time: Mapped[str]


class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    budget: Mapped[int] = mapped_column(default=0)
