import asyncio
import sys
from asyncio import sleep

import typer
from datetime import timedelta
from typing import Annotated

import uvicorn
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status

import schemas
from client import currencies, get_tickers, get_currencies
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from charts import generate_BTC_data
from database import engine
from database import get_session
import crud
from database import Base
# from schemas import CitySchema, UserUpdate
from datetime import datetime
from typing import Iterator
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response


import schedule

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

app = FastAPI()
cli = typer.Typer()



if __name__ == "__main__":
    print("unicorn")
    uvicorn.run(app, host="localhost", port=8000)


# @app.get("/cities/biggest", response_model=list[CitySchema])
# async def get_biggest_cities(session: AsyncSession = Depends(get_session)):
#     cities = await crud.get_biggest_cities(session)
#     return [CitySchema(name=city.name, population=city.population) for city in cities]
#
#
# @app.post("/cities/")
# async def add_city(city: CitySchema, session: AsyncSession = Depends(get_session)):
#     city = crud.add_city(session, city)
#     print(city)
#     try:
#         await session.commit()
#         return city
#     except IntegrityError as ex:
#         await session.rollback()
#         raise DuplicatedEntryError("The city is already stored")


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session)):
    """
    Get a custom token from the database using username from
    the form field. If there is no such user, return the error
    message "incorrect username or password".
    """
    user = await crud.authenticate_user(session=session,
                                  username=form_data.username,
                                  password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
        current_user: Annotated[schemas.User,
                                Depends(crud.get_current_user)]):
    """
    Get the data of an authorized user
    """
    print("OK")
    return current_user


@app.put("/users/me/update", response_model=schemas.User)
async def users_me_update(
        current_user: Annotated[schemas.UserInDB,
                                Depends(crud.get_current_user)],
        user: schemas.UserUpdate,
        session: AsyncSession = Depends(get_session)):
    """
    Get the data of an authorized user
    """
    current_user.username = user.username
    current_user.hashed_password = await crud.get_password_hash(user.password)
    await session.commit()
    return current_user

@app.delete("/users/me/delete", response_model=schemas.User)
async def users_me_delete(
        current_user: Annotated[schemas.User,
                                Depends(crud.get_current_user)],
        session: AsyncSession = Depends(get_session)):
    """
    Get the data of an authorized user
    """
    await session.delete(current_user)
    await session.commit()
    return current_user


@app.post("/users/", response_model=schemas.User)
async def create_user(
        user: schemas.UserCreate,
        session: AsyncSession = Depends(get_session)):
    """
    Creating a user by name and password
    """
    print("Ok")
    db_user = await crud.get_user(session=session, username=user.username)
    print(db_user)
    if db_user:
        raise HTTPException(status_code=400,detail="User already registered")
    print("create")
    result = await crud.create_user(session=session, user=user)
    print(result)
    return result

@app.get("/currency/")
async def add_tickers(
        current_user: Annotated[schemas.User,
                                        Depends(crud.get_current_user)],
        session: AsyncSession = Depends(get_session)):

    tasks = [get_tickers(currency, session)
             for currency in currencies]
    result = await asyncio.gather(*tasks)

    # await session.commit()
    return result
@app.get("/currency/user/me", response_model=list[schemas.Currency])
async def get_all_tickers(
        session: AsyncSession = Depends(get_session)):
    tickers = await get_currencies(session)
    return [schemas.Currency(name=ticker.name, price=ticker.price, time=ticker.time) for ticker in tickers]

@app.get("/BTC", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chart-data")
async def chart_data(request: Request,
                     session: AsyncSession = Depends(get_session)
                     ) -> StreamingResponse:
    response = StreamingResponse(generate_BTC_data(request, session), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


ON_OFF = "off"

async def get_tickers_do(session):
    while ON_OFF == "on":
        await sleep(300)
        tasks = [get_tickers(currency, session)
                 for currency in currencies]
        await asyncio.gather(*tasks)
        await session.commit()


@app.get("/sched/{on_off}")
async def scheduler_func(on_off: str,
                        background_task: BackgroundTasks,
                        session: AsyncSession = Depends(get_session)):
    global ON_OFF
    if ON_OFF != "on" and on_off == "on":
        background_task.add_task(get_tickers_do, session=session)
        ON_OFF = on_off
    if on_off != "on":
        ON_OFF = "off"

    return {"result": ON_OFF}