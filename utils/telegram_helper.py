from aiogram.types import Message, ReplyKeyboardMarkup

from user import User

from user_repository import UserRepository

user_repository = UserRepository()

async def get_active_user(message: Message, reply_markup: ReplyKeyboardMarkup | None = None) -> User|None:

    if message.from_user is None:

        return None

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer(
            "Сначала выполните команду /start",
            reply_markup= reply_markup
        )

        return None

    if not user.is_active:

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= reply_markup
        )

        return None

    return user