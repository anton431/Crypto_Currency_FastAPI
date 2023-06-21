import asyncio
import typer
from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from exceptions import DuplicatedEntryError
from database import init_models
from database import get_session
import crud
from schemas import CitySchema

app = FastAPI()
cli = typer.Typer()


@cli.command()
def db_init_models():
    print("NO Done")
    asyncio.run(init_models())
    print("Done")


@app.get("/cities/biggest", response_model=list[CitySchema])
async def get_biggest_cities(session: AsyncSession = Depends(get_session)):
    cities = await crud.get_biggest_cities(session)
    return [CitySchema(name=c.name, population=c.population) for c in cities]


@app.post("/cities/")
async def add_city(city: CitySchema, session: AsyncSession = Depends(get_session)):
    city = crud.add_city(session, city.name, city.population)
    try:
        await session.commit()
        return city
    except IntegrityError as ex:
        await session.rollback()
        raise DuplicatedEntryError("The city is already stored")


if __name__ == "__main__":
    cli()
