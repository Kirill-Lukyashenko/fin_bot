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
    transfer_confirm_keyboard
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
            "Введите идентификатор счёта числом",
            reply_markup= fsm_navigation_keyboard
        )

        return

    try:

        account_id = int(message.text.strip())

    except ValueError:

        await message.answer(
            "Идентификатор счёта должен быть целочисленным",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if account_id <= 0 :

        await message.answer(
            "Идентификатор счёта должен быть больше нуля",
            reply_markup= fsm_navigation_keyboard
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
            "Указанный счёт отправителя не найден",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if not source_account.is_active:

        await message.answer(
            "Указанный счёт отправителя деактивирован",
            reply_markup= fsm_navigation_keyboard
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

    if message.from_user is None:

        return

    if message.text is None:

        await message.answer(
            "Введите идентификатор счёта числом",
            reply_markup= fsm_navigation_keyboard
        )

        return

    try:

        dest_account_id = int(message.text.strip())

    except ValueError:

        await message.answer(
            "Идентификатор счёта должен быть целочисленным",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if dest_account_id <= 0 :

        await message.answer(
            "Идентификатор счёта должен быть больше нуля",
            reply_markup= fsm_navigation_keyboard
        )

        return

    data = await state.get_data()

    source_account_id = data["source_account_id"]

    if dest_account_id == source_account_id:

        await message.answer(
            "Идентификаторы счёта отправителя и счёта получателя должны быть разными\n\n"
            "Измените идентификатор счёта получателя или вернитесь и измените идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
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

    dest_account = account_repository.get_account_by_id(dest_account_id, user.user_id)

    if dest_account is None:

        await message.answer(
            "Указанный счёт получателя не найден",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if not dest_account.is_active:

        await message.answer(
            "Указанный счёт получателя деактивирован",
            reply_markup= fsm_navigation_keyboard
        )

        return

    source_account = account_repository.get_account_by_id(source_account_id, user.user_id)

    if source_account is None:

        await state.set_state(CreateTransfer.source_account)
    
        await message.answer(
            "Указанный счёт отправителя не найден\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )
    
        return
    
    if not source_account.is_active:

        await state.set_state(CreateTransfer.source_account)
    
        await message.answer(
            "Указанный счёт отправителя деактивирован\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )
    
        return

    if dest_account.currency != source_account.currency:

        await message.answer(
            "Валюта указанных счетов должна быть одинаковая",
            reply_markup= fsm_navigation_keyboard
        )
        return

    await state.update_data(dest_account_id = dest_account_id)

    await state.set_state(CreateTransfer.amount)

    await message.answer(
        "Введите сумму перевода",
        reply_markup= fsm_navigation_keyboard
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

    source_account_id = data["source_account_id"]

    source_account = account_repository.get_account_by_id(source_account_id, user.user_id)

    if source_account is None:

        await state.set_state(CreateTransfer.source_account)

        await message.answer(
            "Указанный счёт отправителя не найден\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if not source_account.is_active:

        await state.set_state(CreateTransfer.source_account)

        await message.answer(
            "Указанный счёт отправителя деактивирован\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if amount > source_account.balance:

        await message.answer(
            "На указанном счёте отправителя недостаточно средств\n\n"
            "Введите меньшую сумму перевода\n"
            f"На счёте доступно: {source_account.balance} {source_account.currency}",
            reply_markup= fsm_navigation_keyboard
        )

        return

    await state.update_data(amount = amount)

    await state.set_state(CreateTransfer.comment)

    await message.answer(
        "Введите комментарий к переводу",
        reply_markup= fsm_navigation_keyboard
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

    data = await state.get_data()

    source_account_id = data["source_account_id"]

    source_account = account_repository.get_account_by_id(source_account_id, user.user_id)

    if source_account is None:

        await state.set_state(CreateTransfer.source_account)

        await message.answer(
            "Указанный счёт отправителя не найден\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if not source_account.is_active:

        await state.set_state(CreateTransfer.source_account)
    
        await message.answer(
            "Указанный счёт отправителя деактивирован\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )
    
        return

    dest_account_id = data["dest_account_id"]

    dest_account = account_repository.get_account_by_id(dest_account_id, user.user_id)

    if dest_account is None:

        await state.set_state(CreateTransfer.dest_account)
    
        await message.answer(
            "Указанный счёт получателя не найден\n\n"
            "Введите другой идентификатор счёта получателя",
            reply_markup= fsm_navigation_keyboard
        )
    
        return
    
    if not dest_account.is_active:

        await state.set_state(CreateTransfer.dest_account)
        
        await message.answer(
            "Указанный счёт получателя деактивирован\n\n"
            "Введите другой идентификатор счёта получателя",
            reply_markup= fsm_navigation_keyboard
        )
        
        return

    if dest_account.currency != source_account.currency:

        await state.set_state(CreateTransfer.dest_account)

        await message.answer(
            "Валюта счетов должна совпадать\n\n"
            "Введите другой идентификатор счёта получателя",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if data["amount"] > source_account.balance:

        await state.set_state(CreateTransfer.amount)

        await message.answer(
            "На счёте отправителя недостаточно средств\n\n"
            f"Доступно: {source_account.balance} {source_account.currency}\n"
            f"Введите другую сумму перевода",
            reply_markup= fsm_navigation_keyboard
        )

        return
    
    await state.set_state(CreateTransfer.confirm)

    await message.answer(
        "Проверьте данные операции\n\n"
        f"Счёт отправителя: №{source_account.object_number} - {source_account.acc_type}\n"
        f"Счёт получателя: №{dest_account.object_number} - {dest_account.acc_type}\n"
        f"Сумма перевода: {data['amount']} {source_account.currency}\n"
        f"Комментарий: {data['comment']}",
        reply_markup= transfer_confirm_keyboard
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

    data = await state.get_data()

    source_account = account_repository.get_account_by_id(data['source_account_id'], user.user_id)

    if source_account is None:
    
        await state.set_state(CreateTransfer.source_account)
    
        await message.answer(
            "Указанный счёт отправителя не найден\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )
    
        return
    
    if not source_account.is_active:
    
        await state.set_state(CreateTransfer.source_account)
        
        await message.answer(
            "Указанный счёт отправителя деактивирован\n\n"
            "Введите другой идентификатор счёта отправителя",
            reply_markup= fsm_navigation_keyboard
        )
        
        return

    dest_account = account_repository.get_account_by_id(data['dest_account_id'], user.user_id)

    if dest_account is None:
    
        await state.set_state(CreateTransfer.dest_account)
        
        await message.answer(
            "Указанный счёт получателя не найден\n\n"
            "Введите другой идентификатор счёта получателя",
            reply_markup= fsm_navigation_keyboard
        )
        
        return
        
    if not dest_account.is_active:
    
        await state.set_state(CreateTransfer.dest_account)
            
        await message.answer(
            "Указанный счёт получателя деактивирован\n\n"
            "Введите другой идентификатор счёта получателя",
            reply_markup= fsm_navigation_keyboard
        )
            
        return

    if dest_account.currency != source_account.currency:

        await state.set_state(CreateTransfer.dest_account)
        
        await message.answer(
            "Валюта счетов должна совпадать\n\n"
            "Введите другой идентификатор счёта получателя",
            reply_markup= fsm_navigation_keyboard
        )
        
        return

    if data["amount"] > source_account.balance:
    
        await state.set_state(CreateTransfer.amount)
    
        await message.answer(
            "На счёте отправителя недостаточно средств\n\n"
            f"Доступно: {source_account.balance} {source_account.currency}\n"
            f"Введите другую сумму перевода",
            reply_markup= fsm_navigation_keyboard
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
    f"Счёт отправителя: №{updated_source.object_number} - {updated_source.acc_type}\n"
    f"Счёт получателя: №{updated_dest.object_number} - {updated_dest.acc_type}\n"
    f"Сумма перевода: {transfer.amount} {updated_source.currency}\n\n"
    f"Новый баланс счёта отправителя: {updated_source.balance} {updated_source.currency}\n"
    f"Новый баланс счёта получателя: {updated_dest.balance} {updated_dest.currency}",
    reply_markup=main_keyboard
)
    
@router.message(CreateTransfer.confirm)
async def invalid_transfer_confirm(message: Message) -> None:

    await message.answer(
        "Используйте кнопку подтверждения перевода",
        reply_markup=transfer_confirm_keyboard
    )