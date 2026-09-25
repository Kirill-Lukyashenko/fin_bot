from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from account_repository import AccountRepository

from utils.telegram_helper import get_active_user

from keyboards import (
    main_keyboard,
    settings_keyboard,
    fsm_navigation_keyboard,
    deactivate_confirm_keyboard
)

router = Router()

account_repository = AccountRepository()

class DeactivateAccount(StatesGroup):

    acc_id = State()
    confirm = State()

@router.message(F.text == "⚙️ Настройки")
async def settings_handler(message : Message, state : FSMContext):

    await state.clear()

    user = await get_active_user(message, main_keyboard)

    if user is None:
        return

    await message.answer(
        "Настройка системы",
        reply_markup= settings_keyboard
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

@router.message(StateFilter(DeactivateAccount), F.text == "❌ Отмена")
async def cancel_deactivate_account(message : Message, state : FSMContext) -> None:

    await state.clear()

    await message.answer(
        "Деактивация счёта отменена",
        reply_markup= settings_keyboard
    )

@router.message(StateFilter(DeactivateAccount), F.text =="⬅️ Назад")
async def back_deactivate_account(message : Message, state : FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == DeactivateAccount.acc_id.state:

        await state.clear()

        await message.answer(
            "Возвращаемся в меню настроек",
            reply_markup= settings_keyboard
        )

        return

    if current_state == DeactivateAccount.confirm.state:

        await state.set_state(DeactivateAccount.acc_id)

        await message.answer(
            "Введите идентификатор деактивируемого счёта",
            reply_markup= fsm_navigation_keyboard
        )

        return

@router.message(F.text == "Деактивировать счёт")
async def deactivate_acc_handler(message : Message, state : FSMContext):

    await state.clear()

    user = await get_active_user(message, settings_keyboard)

    if user is None:
        return

    accounts = account_repository.get_active_accounts(user.user_id)

    if not accounts:

        await message.answer(
            "У вас нет активных счетов",
            reply_markup= settings_keyboard
        )

        return

    await state.set_state(DeactivateAccount.acc_id)

    text = "Ваши активные счета:\n\n"

    for account in accounts:

        if account.product_name is not None:

            text += f"ID:{account.object_number} - {account.product_name}\n"

        else:

            text += f"ID:{account.object_number} - {account.source}\n"

    await message.answer(
        f"{text}"
        "\nВведите идентификатор деактивируемого счёта",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(DeactivateAccount.acc_id)
async def deactivate(message : Message, state : FSMContext) -> None:

    user = await get_active_user(message, settings_keyboard)

    if user is None:
        await state.clear()
        return

    if message.text is None:
        await message.answer("Введите идентификатор счёта числом")
        return

    try:

        acc_id = int(message.text.strip())

    except ValueError:

        await message.answer("Идентификатор должен быть целочисленным")
        return

    if acc_id <= 0 :

        await message.answer("Идентификатор должен быть больше нуля")
        return

    account = account_repository.get_account_by_id(acc_id, user.user_id)

    if account is None:
        await message.answer(
            "Счёт c таким идентификатором не найден", 
            reply_markup= fsm_navigation_keyboard
        )
        return

    if not account.is_active:
        await message.answer(
            "Счёт с таким идентификатором уже деактивирован",
            reply_markup= fsm_navigation_keyboard
        )
        return

    await state.update_data(account_id = account.object_number)

    await state.set_state(DeactivateAccount.confirm)

    message_text = "Проверьте правильность данных\n\n"

    if account.product_name is not None:

        message_text += f"Cчёт: {account.product_name}\n"

    else:

        message_text += f"Cчёт: {account.source}\n"

    await message.answer(
        message_text + 
        f"ID: {account.object_number}\n"
        f"Баланс: {account.balance:,.2f} {account.currency}\n".replace(","," "),
        reply_markup= deactivate_confirm_keyboard
    )

@router.message(DeactivateAccount.confirm, F.text == "✅ Подтвердить деактивацию")
async def confirm_deactivate(message : Message, state : FSMContext):

    user = await get_active_user(message, settings_keyboard)
    
    if user is None:
        await state.clear()
        return

    data = await state.get_data()

    account_id = data["account_id"]

    account = account_repository.get_account_by_id(account_id, user.user_id)

    if account is None:
        await message.answer(
            "Счёт c таким идентификатором не найден", 
            reply_markup= fsm_navigation_keyboard
        )
        return

    if not account.is_active:
        await message.answer(
            "Счёт с таким идентификатором уже деактивирован",
            reply_markup= fsm_navigation_keyboard
        )
        return

    account.is_active = False

    account_repository.update_account(account)

    await state.clear()

    await message.answer(
        f"Счёт с идентификатором {account.object_number} деактивирован",
        reply_markup= settings_keyboard
    )

@router.message(DeactivateAccount.confirm)
async def invalid_deactivate_confirm(message: Message) -> None:

    await message.answer(
        "Используйте кнопку подтверждения деактивации",
        reply_markup=deactivate_confirm_keyboard
    )
    