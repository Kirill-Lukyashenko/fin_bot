from decimal import Decimal
from datetime import date

from transaction import OperationType

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from account_repository import AccountRepository
from transaction_repository import TransactionRepository

from utils.telegram_helper import get_active_user

from keyboards import (
    statistics_keyboard, 
    main_keyboard
)

router = Router()
account_repository = AccountRepository()
transaction_repository = TransactionRepository()

@router.message(F.text == "📊 Статистика")
async def show_options(message: Message, state: FSMContext) -> None:

    await state.clear()

    user = await get_active_user(message, main_keyboard)

    if user is None:
        return

    await message.answer(
        "Получение статистики",
        reply_markup= statistics_keyboard
    )

@router.message(F.text == "Главное меню")
async def main_menu(message: Message, state: FSMContext) -> None:

    await state.clear()

    user = await get_active_user(message, main_keyboard)

    if user is None:
        return

    await message.answer(
        "Возврат в главное меню",
        reply_markup= main_keyboard
    )

@router.message(F.text == "Сумма на всех счетах")
async def total_amount_handler(message: Message, state: FSMContext) -> None:

    user = await get_active_user(message, statistics_keyboard)

    if user is None:
        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if not accounts:

        await message.answer(
            "У вас нет активных счетов",
            reply_markup= statistics_keyboard
        )

        return

    totals: dict[str, Decimal] = {}

    text = "Баланс на счетах: \n\n"

    for account in accounts:

        if account.currency not in totals:

            totals[account.currency] = Decimal("0")

        if account.product_name is not None:

            text += f"{account.product_name} - {account.balance:,.2f} {account.currency}\n".replace(","," ")

        else:

            text += f"{account.source} - {account.balance:,.2f} {account.currency}\n".replace(","," ")

        totals[account.currency] += account.balance

    text += "\nСумма на всех активных счетах:\n\n"

    for currency, total in totals.items():

        text += f"• {total:,.2f} {currency}\n".replace(","," ")

    await message.answer(
        text,
        reply_markup= statistics_keyboard
    )

@router.message(F.text == "Расходы за сегодня")
async def total_expense_by_day(message: Message, state: FSMContext) -> None:

    user = await get_active_user(message, statistics_keyboard)

    if user is None:
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

    totals: dict[str, Decimal] = {}

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

@router.message(F.text == "Доходы за сегодня")
async def total_income_by_day(message: Message, state: FSMContext) -> None:

    user = await get_active_user(message, statistics_keyboard)

    if user is None:
        return

    transactions = transaction_repository.get_transactions_by_period(user.user_id, date.today(), date.today())

    if not transactions:

        await message.answer(
            "Не найдено транзакций за сегодня",
            reply_markup= statistics_keyboard
        )

        return

    message_text = "Доходы за сегодня:\n\n"

    income_found = False

    totals: dict[str, Decimal] = {}

    for transaction in transactions:

        if transaction.operation == OperationType.INCOME:

            income_found  = True

            currency = transaction.account.currency

            if currency not in totals:
                totals[currency] = Decimal("0")

            totals[currency] += transaction.amount

            message_text += f"{transaction.category} - {transaction.amount:,.2f} {transaction.account.currency}\n".replace(","," ")

    if not income_found:

        await message.answer(
            "За сегодня не найдено доходов",
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