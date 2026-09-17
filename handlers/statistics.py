from decimal import Decimal
from datetime import date

from transaction import OperationType

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from user_repository import UserRepository
from account_repository import AccountRepository
from transaction_repository import TransactionRepository

from keyboards import (
    statistics_keyboard, 
    main_keyboard
)

router = Router()
user_repository = UserRepository()
account_repository = AccountRepository()
transaction_repository = TransactionRepository()

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

@router.message(F.text == "Расходы за сегодня")
async def total_expense_by_day(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer(
            "Пользователь не найден",
            reply_markup= statistics_keyboard
        )

        return

    if not user.is_active :

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= statistics_keyboard
        )

        return

    transactions = transaction_repository.get_transactions_by_period(user.user_id, date.today(), date.today())

    if not transactions:

        await message.answer(
            "Не найдено транзакций за сегодня",
            reply_markup= statistics_keyboard
        )

        return

    message_text = "Расходы за сегодня:\n\n"
    expense_found = False

    totals : dict[str, Decimal] = {}

    for transaction in transactions:

        if transaction.operation == OperationType.EXPENSE:

            expense_found = True

            currency = transaction.account.currency

            if currency not in totals:
                totals[currency] = Decimal("0")

            totals[currency] += transaction.amount

            message_text += f"{transaction.category} - {transaction.amount:,.2f} {transaction.account.currency}\n".replace(","," ")

    if not expense_found:

        await message.answer(
            "За сегодня не найдено расходов",
            reply_markup= statistics_keyboard
        )

        return 

    message_text += "\nИтого:\n"

    for currency, total in totals.items():

        message_text += f"• {total:,.2f} {currency}\n".replace(","," ")

    await message.answer(
        message_text,
        reply_markup= statistics_keyboard
    )