from decimal import Decimal

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from user_repository import UserRepository
from account_repository import AccountRepository

from keyboards import (
    statistics_keyboard, 
    main_keyboard
)

router = Router()
user_repository = UserRepository()
account_repository = AccountRepository()

@router.message(F.text == "📊 Статистика")
async def show_options(message : Message, state : FSMContext) -> None:

    await state.clear()

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer(
            "Сначала выполните команду /start"
        )

        return

    if not user.is_active:

        await message.answer(
            "Пользователь деактивирован"
        )

        return

    await message.answer(
        "Получение статистики",
        reply_markup= statistics_keyboard
    )

@router.message(F.text == "Главное меню")
async def main_menu(message : Message, state : FSMContext) -> None:

    await state.clear()

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer(
            "Сначала выполните команду /start"
        )

        return

    if not user.is_active:

        await message.answer(
            "Пользователь деактивирован"
        )

        return

    await message.answer(
        "Возврат в главное меню",
        reply_markup= main_keyboard
    )

@router.message(F.text == "Сумма на всех счетах")
async def total_amount_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer(
            "Сначала выполните команду /start"
        )

        return

    if not user.is_active:

        await message.answer(
            "Пользователь деактивирован"
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if not accounts:

        await message.answer(
            "У вас нет активных счетов",
            reply_markup= statistics_keyboard
        )

        return

    totals : dict[str, Decimal] = {}

    for account in accounts:

        if account.currency not in totals:

            totals[account.currency] = Decimal("0")

        totals[account.currency] += account.balance

    text = "Сумма на всех активных счетах:\n\n"

    for currency, total in totals.items():

        text += f"• {total:,.2f} {currency}\n".replace(","," ")

    await message.answer(
        text,
        reply_markup= statistics_keyboard
    )