# Crypto_Currency_FastAPI

## Описание
Поддерживает все операции CRUD, позволяет регистрировать, изменять и удалять пользователя, осуществлена авторизация по jwt 
токену. Написан клиент, который каждую минуту забирает с биржи текущую цену BTC и ETH, после
чего сохраняет в базу данных тикер валюты. Есть возможность посмотреть последние тикеры валют и 
график отражающий изменение цены валюты со временем на примере BTC. <br>
/docs - документация

## Stack

>Language: __Python 3__<br>
Web framework: __FastAPI__<br>
Database: __PostgreSQL__<br>

Другое: Docker, SQLAlchemy, aiohttp, pytest


## Установка
### Если хотим работать локально
1. Клонируйте репозиторий, пропишите .env и .env-non-dev файлы:
```
git clone https://github.com/anton431/jwt_token_FastAPI.git
```
2. Установите записимости:
```
pip install -r requirements.txt
```
3. Перейдите в директорию currency и проводи миграции:
```
yoyo apply --database postgres://postgres:dbpass@localhost:5432/db ./migrations -b
```
4. Запуск приложения:
```
uvicorn main:app --reload
```
5. Запуск тестов:
```
pytest -v -s tests\tests.py
```

### Создание контейнера приложения
1. Клонируйте репозиторий, пропишите .env и .env-non-dev файлы:
```
git clone https://github.com/anton431/jwt_token_FastAPI.git
```
2. Установите записимости:
```
pip install -r requirements.txt
```
3. Установите пароль в docker-compose в перемнной POSTGRES_PASSWORD, а так же в bash команде:
4. Сборка и запуск:
```
docker-compose build
```
```
docker-compose up
```
5. Есть возможность зайти в pgadmin4:
```
pgadmin4@pgadmin.org
```
```
root
```