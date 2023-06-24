# Create Rocketry app
# import asyncio
#
# from fastapi import Depends
# from rocketry import Rocketry
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from client import get_tickers, currencies
# from database import get_session
# from rocketry.conds import every
#
#
# app = Rocketry(execution="async")
#
#
# # Create some tasks
#
# @app.task(every('2 seconds', based="finish"))
# async def do_things(session: AsyncSession = Depends(get_session)):
#     print("SCHEDULER")
#     tasks = [get_tickers(currency, session)
#              for currency in currencies]
#     result = await asyncio.gather(*tasks)
#
#     await session.commit()
#     return result
#
# if __name__ == "__main__":
#     app.run()