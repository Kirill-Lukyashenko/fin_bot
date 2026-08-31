from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from decimal import Decimal, InvalidOperation

from user import User
from user_repository import UserRepository

from account import Account
from account_repository import AccountRepository

from keyboards import accounts_keyboard, main_keyboard

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

@router.message(F.text == "💰 Счета")
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

@router.message(F.text == "В главное меню")
async def main_menu_handler(message : Message) -> None:
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
        "Главное меню",
        reply_markup= main_keyboard
    )

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

@router.message(CreateAccount.acc_type)
async def create_account_type(message : Message, state : FSMContext) -> None:

    if message.text is None:
        await  message.answer("Введите тип счёта текстом")
        return

    acc_type = message.text.strip()

    if not acc_type:

        await message.answer("Тип счёта не может быть пустым")
        return

    await state.update_data(acc_type = acc_type)

    await state.set_state(CreateAccount.product_name)

    await message.answer(
        "Введите название счёта\n"
        "Например: KASPI_GOLD, BCC_SILVER и т.д.\n\n"
        "Если названия нет, отправьте -"
    )

@router.message(CreateAccount.product_name)
async def create_account_product_name(message : Message, state : FSMContext) -> None:

    if message.text is None:
        await message.answer("Введите название текстом")
        return

    product_name = message.text.strip()

    if product_name == "-":
        product_name = None

    await state.update_data(product_name = product_name)

    await state.set_state(CreateAccount.requisites)

    await message.answer(
        "Введите реквизиты счёта\n\n"
        "Если указывать не хотите, отправьте -"
    )

@router.message(CreateAccount.requisites)
async def create_account_requisites(message : Message, state : FSMContext) -> None:

    if message.text is None:
        await message.answer("Введите реквизиты текстом")
        return

    requisites = message.text.strip()

    if requisites == "-":
        requisites = None

    await state.update_data(requisites = requisites)

    await state.set_state(CreateAccount.currency)

    await message.answer(
        "Введите валюту счёта\n"
        "Например: KZT, USD, RUB"
    )

@router.message(CreateAccount.currency)
async def create_account_currency(message : Message, state : FSMContext) -> None:

    if message.text is None:
        await message.answer("Введите валюту счёта текстом")
        return

    currency = message.text.strip().upper()

    if not currency:
        await message.answer("Валюта не может быть пустой")
        return

    await state.update_data(currency = currency)

    await state.set_state(CreateAccount.balance)

    await message.answer(
        "Введите текущий баланс счёта.\n"
        "Например: 150000 или 125000.50"
    )

@router.message(CreateAccount.balance)
async def create_account_balance(message : Message, state : FSMContext) -> None:

    if message.text is None:
        await message.answer("Введите баланс числом")
        return

    try:

        balance = Decimal(message.text.strip().replace(",","."))

    except InvalidOperation:

        await message.answer(
            "Некорректный баланс\n"
            "Например: 150000 или 125000.50"
        )

        return

    if not balance.is_finite():
        await message.answer("Баланс должен быть конечным числом")
        return

    if balance < 0:
        await message.answer("Баланс не может быть отрицательным")
        return

    if message.from_user is None:
        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer("Пользователь не найден")

        return

    if not user.is_active:

        await state.clear()

        await message.answer("Пользователь деактивирован")

        return

    data = await state.get_data()

    account = Account(
        object_number= None,
        user_id= user.user_id,
        source= data["source"],
        acc_type= data["acc_type"],
        product_name= data["product_name"],
        requisites= data["requisites"],
        balance= balance,
        currency= data["currency"],
        limit= None,
        is_active= True
    )

    account_id = account_repository.add_account(account)

    await state.clear()

    await message.answer(
        "Счёт успешно создан\n\n"
        f"ID: {account_id}\n"
        f"Источник:  {account.source}\n"
        f"Баланс: {account.balance} {account.currency}",
        reply_markup= accounts_keyboard
    )