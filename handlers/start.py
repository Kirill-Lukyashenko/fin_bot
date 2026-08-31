from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from user import User
from user_repository import UserRepository

from keyboards import main_keyboard


router = Router()

user_repository = UserRepository()

@router.message(CommandStart())
async def start_handler(message : Message, state : FSMContext) -> None:

    await state.clear()

    if message.from_user is None:
        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        user = User(telegram_user_id= telegram_user_id)

        user_repository.add_user(user)

        await message.answer(
            "Добро пожаловать!\n"
            "Новый пользователь зарегестрирован.",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await message.answer("Пользователь деактивирован!")
        return

    await message.answer(
        "Главное меню",
        reply_markup= main_keyboard
    )