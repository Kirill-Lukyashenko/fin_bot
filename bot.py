import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import create_tables
from account_repository import AccountRepository

from handlers.start import router as start_router
from handlers.accounts import router as accounts_router
from handlers.transactions import router as transactions_router
from handlers.transfers import router as transfers_router
from handlers.statistics import router as statistics_router
from handlers.settings import router as settings_router

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
account_service = AccountRepository()

async def main() -> None:

    create_tables()

    dp.include_router(start_router)
    dp.include_router(accounts_router)
    dp.include_router(transactions_router)
    dp.include_router(transfers_router)
    dp.include_router(statistics_router)
    dp.include_router(settings_router)

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())