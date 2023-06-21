from sqlalchemy.ext.asyncio import AsyncSession

import models
from models import *
from schemas import CitySchema


async def get_all_cities(session: AsyncSession) -> list[City]:
    cities = session.query(models.City).all()
    return cities


def add_city(session: AsyncSession, city: CitySchema):

    new_city = models.City(name=city.name,
                            population=city.population)
    session.add(new_city)
    session.commit()
    session.refresh(new_city)

    return new_city