import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import create_tables

from handlers.start import router as start_router
from handlers.accounts import router as accounts_router
from handlers.transactions import router as transactions_router

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def main() -> None:

    create_tables()

    dp.include_router(start_router)
    dp.include_router(accounts_router)
    dp.include_router(transactions_router)

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())