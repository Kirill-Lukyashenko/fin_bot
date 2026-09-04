from datetime import date
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from transaction import Transaction, OperationType

from transaction_service import TransactionService
from account_repository import AccountRepository
from user_repository import UserRepository

from keyboards import (
    main_keyboard,
    fsm_navigation_keyboard
)

router = Router()

user_repository = UserRepository()

transaction_service = TransactionService()

account_repository = AccountRepository()

class CreateIncome(StatesGroup):

    account_id = State()
    ammount = State()
    category = State()
    comment = State()
    confirm = State()

@router.message(F.text == "📥 Доход")
async def create_income_handler(message : Message, state : FSMContext):

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer("Сначала выполните команду /start")

        return

    if not user.is_active:

        await message.answer("Пользователь деактивирован!")

        return

    await state.clear()

    await state.set_state(CreateIncome.account_id)

    await message.answer(
        "Введите ID счёта на который поступил доход",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateIncome.account_id)
async def income_account(message : Message, state : FSMContext):

    if message.from_user is None:
        return

    if message.text is None:

        await message.answer("Введите идентификатор счёта числом")

        return

    try:

        account_id = int(message.text.strip())

    except ValueError:

        await message.answer("Идентификатор должен быть целым числом")

        return

    if account_id <= 0 :

        await message.answer("Идентификатор должен быть больше нуля")

        return

    telegram_user_id = message.from_user.id
    
    user = user_repository.get_user_by_telegram_id(telegram_user_id)
    
    if user is None:

        await state.clear()
    
        await message.answer("Пользователь не найден")
    
        return
    
    account = AccountRepository.get_account_by_id(account_id, user.user_id)

    if account is None:

        await message.answer("Счёт с таким идентификатором не найден")

        return

    if not account.is_active:

        await message.answer("Аккаунт деактивирован")

        return

    await state.update_data(account_id = account_id)

    await state.set_state(CreateIncome.ammount)

    
    

    



    