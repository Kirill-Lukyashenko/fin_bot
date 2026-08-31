from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from user import User
from user_repository import UserRepository

from account import Account
from account_repository import AccountRepository

from keyboards import accounts_keyboard

router = Router()

user_repository = UserRepository()
account_repository = AccountRepository()

class CreateAccount(StatesGroup):

    source = State()
    acc_type = State()
    product_name = State()
    requisites = State()
    currency = State()
    balance = State()

@router.message(F.text == "Счета")
async def accounts_handler(message : Message) -> None:

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

    await message.answer(
        "Работа с текущими счетами",
        reply_markup= accounts_keyboard
    )

@router.message(F.text == "Получить список счетов")
async def get_accounts_handler(message : Message) -> None:

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

    accounts = account_repository.get_active_accounts(user.user_id)

    if not accounts:

        await message.answer("У вас нет активных счетов")
        return

    message_text = (f"Найденое количество счетов: {len(accounts)} \n\n")

    for number, account in enumerate(accounts, start=1):

        message_text += (
            f"{number}. {account.source}\n"
            f"Тип: {account.acc_type}\n"
                         )

        if account.product_name is not None:

            message_text += (
                f"Продукт: {account.product_name}\n"
            )

        message_text += (
            f"Баланс: {account.balance} {account.currency}\n\n"
        )

        await message.answer(message_text)

@router.message(F.text == "Создать счёт")
async def create_account_handler(message : Message, state : FSMContext) -> None:

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

    await state.set_state(CreateAccount.source)

    await message.answer(
        "Введите источник счета\n"
        "Например: KASPI, BCC, FREEDOM, НАЛИЧКА и т.д."
                         )

@router.message(CreateAccount.source)
async def create_account_source(message : Message, state : FSMContext) -> None:

    if message.text is None:
        await message.answer("Введите источник текстом")
        return

    source = message.text.strip()

    if not source:
        await message.answer("Источник не может быть пустым")
        return

    await state.update_data(source = source)

    await state.set_state(CreateAccount.acc_type)

    await message.answer(
            "Введите тип счета\n"
            "Например: карта, кредитка, наличка и т.д."
                             )