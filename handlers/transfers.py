from datetime import date
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

from user_repository import UserRepository
from account_repository import AccountRepository

from keyboards import (
    main_keyboard,
    fsm_navigation_keyboard,
    transfer_confirm_keyboard
)

router = Router()

user_repository = UserRepository()
account_repository = AccountRepository()

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


    await state.set_state(CreateTransfer.source_account)

    await message.answer(
        "Введите идентификатор счёта с которого совершается перевод",
        reply_markup= fsm_navigation_keyboard
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

        await state.set_state(CreateTransfer.source_account)

        await message.answer(
            "Введите идентификатор счёта с которого совершается перевод",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateTransfer.amount.state:

        await state.set_state(CreateTransfer.dest_account)

        await message.answer(
            "Введите идентификатор счёта на который совершается перевод",
            reply_markup= fsm_navigation_keyboard
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

        await message.answer(
            "Введите идентификатор счёта числом"
        )

        return

    try:

        account_id = int(message.text.strip())

    except ValueError:

        await message.answer(
            "Идентификатор счёта должен быть целочисленным"
        )

        return

    if account_id <= 0 :

        await message.answer(
            "Идентификатор счёта должен быть больше нуля"
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

    source_account = account_repository.get_account_by_id(account_id, user.user_id)

    if source_account is None:

        await message.answer(
            "Счёт с введённым идентификатором не найден"
        )

        return

    if not source_account.is_active:

        await message.answer(
            "Счёт деактивирован"
        )

        return

    await state.update_data(source_account_id = account_id)

    await state.set_state(CreateTransfer.dest_account)

    await message.answer(
        "Введите идентификатор счёта на который совершается перевод",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateTransfer.dest_account)
async def dest_acc_handler(message : Message, state : FSMContext) -> None:

    pass