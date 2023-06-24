import typer
from datetime import timedelta
from typing import Annotated
import asyncio

import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

import schemas
from client import get_ticker, get_currencies
from config import ACCESS_TOKEN_EXPIRE_MINUTES, currencies
from charts import generate_BTC_data
from database import get_session
import crud

templates = Jinja2Templates(directory="templates")

app = FastAPI()
cli = typer.Typer()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)


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
    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    current_user.hashed_password = await crud.get_password_hash(
        user.password)
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
    db_user = await crud.get_user(session=session,
                                  username=user.username)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="User already registered")
    result = await crud.create_user(session=session, user=user)

    return result


@app.get("/currency/")
async def get_current_tickers(
        current_user: Annotated[schemas.User,
                                Depends(crud.get_current_user)],
        session: AsyncSession = Depends(get_session)):
    tasks = [get_ticker(currency, session)
             for currency in currencies]
    result = await asyncio.gather(*tasks)

    return result


@app.get("/currencies/", response_model=list[schemas.Currency])
async def get_all_tickers(
        session: AsyncSession = Depends(get_session)):
    """
    Get all tickers of currencies for all time
    """
    tickers = await get_currencies(session)
    return [schemas.Currency(name=ticker.name, price=ticker.price,
                             time=ticker.time) for ticker in tickers]


@app.get("/BTC", response_class=HTMLResponse)
async def chart_BTC(request: Request) -> Response:
    """
    Builds a BTC chart for all time
    """
    return templates.TemplateResponse("index.html",
                                      {"request": request})


@app.get("/chart-data/BTC")
async def chart_data_BTC(
        session: AsyncSession = Depends(
            get_session)) -> StreamingResponse:
    """
    Outputs data for the BTC chart
    """
    response = StreamingResponse(generate_BTC_data(session),
                                 media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


ON_OFF = "off"


async def get_tickers_do(session):
    """
    Get tickets from derbit.com and writes them to the database every 5 minutes
    """
    while ON_OFF == "on":
        await asyncio.sleep(300)
        tasks = [get_ticker(currency, session)
                 for currency in currencies]
        await asyncio.gather(*tasks)
        await session.commit()


@app.get("/add_tasks/{on_off}")
async def scheduler_tasks(on_off: str,
                          background_task: BackgroundTasks,
                          session: AsyncSession = Depends(get_session)):
    """
    Enables and disables the function "get_tickers_do"
    """
    global ON_OFF
    if ON_OFF != "on" and on_off == "on":
        background_task.add_task(get_tickers_do, session=session)
        ON_OFF = on_off
    if on_off != "on":
        ON_OFF = "off"

    return {"result": ON_OFF}