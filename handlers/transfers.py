from datetime import date
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

from user_repository import UserRepository
from account_repository import AccountRepository
from transfer import Transfer
from transaction_service import TransactionService

from keyboards import (
    main_keyboard,
    fsm_navigation_keyboard,
    transfer_confirm_keyboard,
    accounts_select_keyboard
)

router = Router()

user_repository = UserRepository()
account_repository = AccountRepository()
service = TransactionService()

class CreateTransfer(StatesGroup):

    source_account = State()
    dest_account = State()
    amount = State()
    comment = State()
    confirm = State()

@router.message(F.text == "♻️ Перевод")
async def create_transfer(message : Message, state : FSMContext) -> None:

    await state.clear()

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer(
            "Сначала выполните команду /start",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if len(accounts) <2:

        await message.answer(
            "Для перевода необходимо минимум два активных счёта",
            reply_markup= main_keyboard
        )

        return

    accounts_map : dict[str,int] = {}

    for account in accounts:
        if account.product_name is not None:
            button_text = f"{account.source}\n{account.product_name}"
        else:
            button_text = f"{account.source}"

        accounts_map[button_text] = account.object_number

    await state.clear()

    await state.update_data(accounts_map= accounts_map)

    await state.set_state(CreateTransfer.source_account)

    await message.answer(
        "Выберите счёт с которого совершается перевод",
        reply_markup= accounts_select_keyboard(accounts)
    )

@router.message(StateFilter(CreateTransfer), F.text == "❌ Отмена")
async def cancel_transfer(message : Message, state : FSMContext) -> None:

    await state.clear()

    await message.answer(
        "Отмена попытки перевода",
        reply_markup= main_keyboard
    )

@router.message(StateFilter(CreateTransfer), F.text == "⬅️ Назад")
async def back_transfer(message : Message, state : FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == CreateTransfer.source_account.state:

        await state.clear()

        await message.answer(
            "Отмена перевода и возврат в главное меню",
            reply_markup= main_keyboard
        )

        return

    if current_state == CreateTransfer.dest_account.state:

        if message.from_user is None:
            return

        telegram_user_id = message.from_user.id

        user = user_repository.get_user_by_telegram_id(telegram_user_id)

        if user is None:

            await state.clear()

            await message.answer(
                "Пользователь не найден",
                reply_markup= main_keyboard
            )

            return

        accounts = account_repository.get_active_accounts(user.user_id)

        if len(accounts) <2:

            await state.clear()

            await message.answer(
                "Для перевода необходимо минимум два активных счёта",
                reply_markup= main_keyboard
            )

            return

        accounts_map: dict[str, int] = {}

        for account in accounts:

            if account.product_name is not None:
                button_text = f"{account.source}\n{account.product_name}"
            else:
                button_text = f"{account.source}"

            accounts_map[button_text] = account.object_number

        await state.update_data(accounts_map = accounts_map)

        await state.set_state(CreateTransfer.source_account)

        await message.answer(
            "Выберите счёт с которого совершается перевод",
            reply_markup= accounts_select_keyboard(accounts)
        )

        return

    if current_state == CreateTransfer.amount.state:

        if message.from_user is None:
            return

        telegram_user_id = message.from_user.id

        user = user_repository.get_user_by_telegram_id(telegram_user_id)

        if user is None:

            await state.clear()

            await message.answer(
                "Пользователь не найден",
                reply_markup= main_keyboard
            )

            return

        accounts = account_repository.get_active_accounts(user.user_id)

        if len(accounts) <2:

            await state.clear()

            await message.answer(
                "Для перевода необходимо минимум два активных счёта",
                reply_markup= main_keyboard
            )

            return

        accounts_map: dict[str, int] = {}

        for account in accounts:

            if account.product_name is not None:
                button_text = f"{account.source}\n{account.product_name}"
            else:
                button_text = f"{account.source}"

            accounts_map[button_text] = account.object_number

        await state.update_data(accounts_map = accounts_map)

        await state.set_state(CreateTransfer.dest_account)

        await message.answer(
            "Выберите счёт на который совершается перевод",
            reply_markup= accounts_select_keyboard(accounts)
        )

        return

    if current_state == CreateTransfer.comment.state:

        await state.set_state(CreateTransfer.amount)

        await message.answer(
            "Введите сумму перевода",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateTransfer.confirm.state:

        await state.set_state(CreateTransfer.comment)

        await message.answer(
            "Введите комментарий к переводу",
            reply_markup= fsm_navigation_keyboard
        )

        return

@router.message(CreateTransfer.source_account)
async def source_acc_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:
        return

    if message.text is None:
        return

    data = await state.get_data()

    accounts_map = data.get("accounts_map",{})

    account_id = accounts_map.get(message.text)

    if account_id is None:

        await message.answer(
            "Выберите счёт с помощью кнопки"
        )

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active : 

        await state.clear()

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if len(accounts) < 2:

        await state.clear()

        await message.answer(
            "Для перевода необходимо минимум два активных счёта",
            reply_markup=main_keyboard
        )

        return

    accounts_map: dict[str, int] = {}

    for account in accounts:

        if account.product_name is not None:
            button_text = (
                f"{account.source}\n"
                f"{account.product_name}"
            )

        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.update_data(
        accounts_map=accounts_map
    )

    source_account = account_repository.get_account_by_id(account_id, user.user_id)

    if source_account is None:

        await message.answer(
            "Указанный счёт отправителя не найден\n"
            "Выберите другой счёт",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not source_account.is_active:

        await message.answer(
            "Указанный счёт отправителя деактивирован\n"
            "Выберите другой счёт",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    await state.update_data(source_account_id = account_id)

    await state.set_state(CreateTransfer.dest_account)

    await message.answer(
        "Выберите счёт на который совершается перевод",
        reply_markup= accounts_select_keyboard(accounts)
    )

@router.message(CreateTransfer.dest_account)
async def dest_acc_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    if message.text is None:
        return

    data = await state.get_data()

    accounts_map = data.get("accounts_map",{})

    dest_account_id = accounts_map.get(message.text)

    if dest_account_id is None:

        await message.answer(
            "Выберите счёт с помощью кнопки"
        )

        return

    source_account_id = data["source_account_id"]

    if dest_account_id == source_account_id:

        await message.answer(
            "Счёт отправителя и счёт получателя должны быть разными\n\n"
            "Выберите другой счёт получателя"
        )

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if len(accounts) < 2:

        await state.clear()

        await message.answer(
            "Для перевода необходимо минимум два активных счёта",
            reply_markup=main_keyboard
        )

        return

    accounts_map: dict[str, int] = {}

    for account in accounts:

        if account.product_name is not None:
            button_text = (
                f"{account.source}\n"
                f"{account.product_name}"
            )
        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.update_data(
        accounts_map=accounts_map
    )

    dest_account = account_repository.get_account_by_id(
        dest_account_id,
        user.user_id
    )

    if dest_account is None:

        await message.answer(
            "Счёт получателя больше не найден.\n\n"
            "Выберите другой счёт.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not dest_account.is_active:

        await message.answer(
            "Счёт получателя деактивирован.\n\n"
            "Выберите другой счёт.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    source_account = account_repository.get_account_by_id(
        source_account_id,
        user.user_id
    )

    if source_account is None:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя больше не найден.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not source_account.is_active:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя деактивирован.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if dest_account.currency != source_account.currency:

        await message.answer(
            "Валюта счетов должна совпадать.\n\n"
            f"Счёт отправителя: {source_account.currency}\n"
            f"Счёт получателя: {dest_account.currency}\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    await state.update_data(
        dest_account_id=dest_account_id
    )

    await state.set_state(
        CreateTransfer.amount
    )

    await message.answer(
        "Введите сумму перевода",
        reply_markup=fsm_navigation_keyboard
    )

@router.message(CreateTransfer.amount)
async def amount_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    if message.text is None:

        await message.answer(
            "Введите сумму перевода числом",
            reply_markup= fsm_navigation_keyboard
        )

        return

    try:

        amount = Decimal(message.text.strip().replace(",","."))

    except InvalidOperation:

        await message.answer(
            "Некорректно указанная сумма",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if not amount.is_finite():

        await message.answer(
            "Сумма должна быть конечным числом",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if amount <= 0:

        await message.answer(
            "Сумма должна быть больше нуля",
            reply_markup= fsm_navigation_keyboard
        )

        return

    data = await state.get_data()

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if len(accounts) < 2:

        await state.clear()

        await message.answer(
            "Для перевода необходимо минимум два активных счёта",
            reply_markup=main_keyboard
        )

        return

    accounts_map: dict[str, int] = {}

    for account in accounts:

        if account.product_name is not None:
            button_text = (
                f"{account.source}\n"
                f"{account.product_name}"
            )
        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.update_data(accounts_map=accounts_map)

    source_account_id = data["source_account_id"]

    source_account = account_repository.get_account_by_id(
        source_account_id,
        user.user_id
    )

    if source_account is None:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя больше не найден.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not source_account.is_active:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя деактивирован.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if amount > source_account.balance:

        await message.answer(
            "На указанном счёте отправителя недостаточно средств\n\n"
            "Введите меньшую сумму перевода\n"
            f"На счёте доступно: "
            f"{source_account.balance} "
            f"{source_account.currency}",
            reply_markup=fsm_navigation_keyboard
        )

        return

    await state.update_data(
        amount=amount
    )

    await state.set_state(
        CreateTransfer.comment
    )

    await message.answer(
        "Введите комментарий к переводу",
        reply_markup=fsm_navigation_keyboard
    )

@router.message(CreateTransfer.comment)
async def comment_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    if message.text is None:

        await message.answer(
            "Введите комментарий текстом",
            reply_markup= fsm_navigation_keyboard
        )

        return

    comment = message.text.strip()

    if not comment:

        await message.answer(
            "Комментарий не может быть пустым",
            reply_markup= fsm_navigation_keyboard
        )

        return

    await state.update_data(comment = comment)

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if len(accounts) < 2:

        await state.clear()

        await message.answer(
            "Для перевода необходимо минимум два активных счёта",
            reply_markup=main_keyboard
        )

        return

    accounts_map: dict[str, int] = {}

    for account in accounts:

        if account.product_name is not None:
            button_text = (
                f"{account.source}\n"
                f"{account.product_name}"
            )
        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.update_data(
        accounts_map=accounts_map
    )

    data = await state.get_data()

    source_account_id = data["source_account_id"]

    source_account = account_repository.get_account_by_id(
        source_account_id,
        user.user_id
    )

    if source_account is None:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя больше не найден.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not source_account.is_active:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя деактивирован.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    dest_account_id = data["dest_account_id"]

    dest_account = account_repository.get_account_by_id(
        dest_account_id,
        user.user_id
    )

    if dest_account is None:

        await state.set_state(
            CreateTransfer.dest_account
        )

        await message.answer(
            "Счёт получателя больше не найден.\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not dest_account.is_active:

        await state.set_state(
            CreateTransfer.dest_account
        )

        await message.answer(
            "Счёт получателя деактивирован.\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if dest_account.currency != source_account.currency:

        await state.set_state(
            CreateTransfer.dest_account
        )

        await message.answer(
            "Валюта счетов должна совпадать.\n\n"
            f"Счёт отправителя: {source_account.currency}\n"
            f"Счёт получателя: {dest_account.currency}\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if data["amount"] > source_account.balance:

        await state.set_state(
            CreateTransfer.amount
        )

        await message.answer(
            "На счёте отправителя недостаточно средств\n\n"
            f"Доступно: {source_account.balance} "
            f"{source_account.currency}\n"
            "Введите другую сумму перевода",
            reply_markup=fsm_navigation_keyboard
        )

        return

    await state.set_state(
        CreateTransfer.confirm
    )

    await message.answer(
        "Проверьте данные операции\n\n"
        f"Счёт отправителя: №{source_account.object_number} - "
        f"{source_account.source}\n"
        f"Счёт получателя: №{dest_account.object_number} - "
        f"{dest_account.source}\n"
        f"Сумма перевода: {data['amount']} "
        f"{source_account.currency}\n"
        f"Комментарий: {data['comment']}",
        reply_markup=transfer_confirm_keyboard
    )

@router.message(CreateTransfer.confirm, F.text == "✅ Подтвердить перевод")
async def confirm_transfer_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if len(accounts) < 2:

        await state.clear()

        await message.answer(
            "Для перевода необходимо минимум два активных счёта",
            reply_markup=main_keyboard
        )

        return

    accounts_map: dict[str, int] = {}

    for account in accounts:

        if account.product_name is not None:
            button_text = (
                f"{account.source}\n"
                f"{account.product_name}"
            )
        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.update_data(
        accounts_map=accounts_map
    )

    data = await state.get_data()

    source_account = account_repository.get_account_by_id(
        data["source_account_id"],
        user.user_id
    )

    if source_account is None:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя больше не найден.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not source_account.is_active:

        await state.set_state(
            CreateTransfer.source_account
        )

        await message.answer(
            "Счёт отправителя деактивирован.\n\n"
            "Выберите другой счёт отправителя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    dest_account = account_repository.get_account_by_id(
        data["dest_account_id"],
        user.user_id
    )

    if dest_account is None:

        await state.set_state(
            CreateTransfer.dest_account
        )

        await message.answer(
            "Счёт получателя больше не найден.\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if not dest_account.is_active:

        await state.set_state(
            CreateTransfer.dest_account
        )

        await message.answer(
            "Счёт получателя деактивирован.\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if dest_account.currency != source_account.currency:

        await state.set_state(
            CreateTransfer.dest_account
        )

        await message.answer(
            "Валюта счетов должна совпадать.\n\n"
            f"Счёт отправителя: {source_account.currency}\n"
            f"Счёт получателя: {dest_account.currency}\n\n"
            "Выберите другой счёт получателя.",
            reply_markup=accounts_select_keyboard(accounts)
        )

        return

    if data["amount"] > source_account.balance:

        await state.set_state(
            CreateTransfer.amount
        )

        await message.answer(
            "На счёте отправителя недостаточно средств\n\n"
            f"Доступно: {source_account.balance} "
            f"{source_account.currency}\n"
            "Введите другую сумму перевода",
            reply_markup=fsm_navigation_keyboard
        )

        return
    
    try:

        transfer = Transfer(
            action_date= date.today(),
            source_account_id= data['source_account_id'],
            dest_account_id= data['dest_account_id'],
            amount= data['amount'],
            comment= data['comment'],
            transfer_id= None,
            is_active= True
        )

        service.execute_transfer(transfer, user.user_id)

    except (ValueError, TypeError) as error:

        await message.answer(
            "Не удалось выполнить перевод\n"
            f"{error}",
            reply_markup= transfer_confirm_keyboard
        )

        return

    updated_source = account_repository.get_account_by_id(data['source_account_id'], user.user_id)

    updated_dest = account_repository.get_account_by_id(data['dest_account_id'], user.user_id)

    await state.clear()

    await message.answer(
    "Перевод успешно выполнен!\n\n"
    f"Счёт отправителя: №{updated_source.object_number} - {updated_source.source}\n"
    f"Счёт получателя: №{updated_dest.object_number} - {updated_dest.source}\n"
    f"Сумма перевода: {transfer.amount} {updated_source.currency}\n\n"
    f"Баланс счёта отправителя: {updated_source.balance:,.2f} {updated_source.currency}\n"
    f"Баланс счёта получателя: {updated_dest.balance:,.2f} {updated_dest.currency}".replace(","," "),
    reply_markup=main_keyboard
)
    
@router.message(CreateTransfer.confirm)
async def invalid_transfer_confirm(message: Message) -> None:

    await message.answer(
        "Используйте кнопку подтверждения перевода",
        reply_markup=transfer_confirm_keyboard
    )