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
    fsm_navigation_keyboard,
    operation_confirm_keyboard,
    accounts_select_keyboard
)

router = Router()

user_repository = UserRepository()

transaction_service = TransactionService()

account_repository = AccountRepository()

class CreateIncome(StatesGroup):

    account_id = State()
    amount = State()
    category = State()
    comment = State()
    confirm = State()

class CreateExpense(StatesGroup):

    account_id = State()
    amount = State()
    category = State()
    comment = State()
    confirm = State()

@router.message(F.text == "📥 Доход")
async def create_income_handler(message : Message, state : FSMContext) -> None:

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

        await message.answer(
            "У вас нет активных счетов"
        )

        return

    accounts_map : dict[str,int]= {}

    for account in accounts:

        if account.product_name is not None:
            button_text = f"{account.source}\n{account.product_name}"
        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.clear()

    await state.update_data(accounts_map = accounts_map)

    await state.set_state(CreateIncome.account_id)

    await message.answer(
        "Выберите счёт на который поступает доход",
        reply_markup= accounts_select_keyboard(accounts)
    )

@router.message(F.text == "📤 Расход")
async def create_expense_handler(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await message.answer("Сначала выполните команду /start")

        return

    if not user.is_active :

        await message.answer("Пользователь деактивирован!")

        return

    accounts = account_repository.get_active_accounts(user.user_id)
    
    if not accounts:
    
        await message.answer(
            "У вас нет активных счетов"
        )
    
        return

    accounts_map : dict[str,int]= {}

    for account in accounts:

        if account.product_name is not None:
            button_text = f"{account.source}\n{account.product_name}"
        else:
            button_text = account.source

        accounts_map[button_text] = account.object_number

    await state.clear()

    await state.update_data(accounts_map = accounts_map)

    await state.set_state(CreateExpense.account_id)

    await message.answer(
        "Выберите счёт с которого расходуются средства",
        reply_markup= accounts_select_keyboard(accounts)
    )

@router.message(StateFilter(CreateIncome, CreateExpense), F.text == "❌ Отмена")
async def cancel_operation(message : Message, state : FSMContext) -> None:

    await state.clear()

    await message.answer(
        "Отмена операции",
        reply_markup= main_keyboard
    )

@router.message(StateFilter(CreateIncome,CreateExpense), F.text == "⬅️ Назад")
async def back_operation(message : Message, state : FSMContext) -> None:

    current_state = await state.get_state()

    if current_state in (
        CreateExpense.account_id.state, 
        CreateIncome.account_id.state
    ):

        await state.clear()

        await message.answer(
            "Возвращаемся в главное меню",
            reply_markup= main_keyboard
        )

        return

    if current_state == CreateExpense.amount.state:

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

        if not accounts:

            await state.clear()
        
            await message.answer(
                "У вас нет активных счетов",
                reply_markup= main_keyboard
            )
        
            return

        accounts_map : dict[str,int]= {}

        for account in accounts:

            if account.product_name is not None:
                button_text = f"{account.source}\n{account.product_name}"
            else:
                button_text = account.source

            accounts_map[button_text] = account.object_number

        await state.update_data(accounts_map = accounts_map)

        await state.set_state(CreateExpense.account_id)

        await message.answer(
            "Выберите счёт, с которого произведён расход",
            reply_markup= accounts_select_keyboard(accounts)
        )

        return

    if current_state == CreateIncome.amount.state:

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

        if not accounts:
        
            await state.clear()
                
            await message.answer(
                "У вас нет активных счетов",
                reply_markup= main_keyboard
            )
                
            return

        accounts_map : dict[str,int]= {}
        
        for account in accounts:
        
            if account.product_name is not None:
                button_text = f"{account.source}\n{account.product_name}"
            else:
                button_text = account.source
        
            accounts_map[button_text] = account.object_number
        
        await state.update_data(accounts_map = accounts_map)
    
        await state.set_state(CreateIncome.account_id)
    
        await message.answer(
            "Выберите счёт, на который поступил доход",
            reply_markup= accounts_select_keyboard(accounts)
        )
    
        return

    if current_state == CreateExpense.category.state:

        await state.set_state(CreateExpense.amount)

        await message.answer(
            "Введите сумму расхода",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateIncome.category.state:
        await state.set_state(CreateIncome.amount)

        await message.answer(
            "Введите сумму дохода",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateExpense.comment.state:

        await state.set_state(CreateExpense.category)

        await message.answer(
            "Введите категорию расхода",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateIncome.comment.state:
        await state.set_state(CreateIncome.category)

        await message.answer(
            "Введите категорию дохода",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateExpense.confirm.state:

        await state.set_state(CreateExpense.comment)

        await message.answer(
            "Введите комментарий для расхода",
            reply_markup= fsm_navigation_keyboard
        )

        return

    if current_state == CreateIncome.confirm.state:
        await state.set_state(CreateIncome.comment)

        await message.answer(
            "Введите комментарий для дохода",
            reply_markup= fsm_navigation_keyboard
        )

        return
    
@router.message(CreateIncome.account_id)
async def income_account(message : Message, state : FSMContext) -> None:

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

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован",
            reply_markup= main_keyboard
        )

        return
    
    account = account_repository.get_account_by_id(account_id, user.user_id)

    if account is None:

        await message.answer("Счёт с таким идентификатором не найден")

        return

    if not account.is_active:

        await message.answer("Счёт деактивирован")

        return

    await state.update_data(account_id = account_id)

    await state.set_state(CreateIncome.amount)

    await message.answer(
        f"Счёт c идентификатором: {account.object_number}\n"
        f"Счёт: {account.source} \n"
        f"Текущий баланс: {account.balance} {account.currency}\n"
        "Введите сумму дохода",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateExpense.account_id)
async def expense_account(message : Message, state : FSMContext) -> None:

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

    telegram_user_id  = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден!",
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован!",
            reply_markup= main_keyboard
        )

        return

    account = account_repository.get_account_by_id(account_id, user.user_id)

    if account is None:

        await message.answer("Счёт с таким идентификатором не найден")

        return

    if not account.is_active:

        await message.answer("Счёт деактивирован")

        return

    await state.update_data(account_id = account_id)

    await state.set_state(CreateExpense.amount)

    await message.answer(
        f"Счёт c идентификатором: {account.object_number}\n"
        f"Счёт: {account.source} \n"
        f"Текущий баланс: {account.balance} {account.currency}\n"
        "Введите сумму расхода",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateIncome.amount)
async def income_amount(message : Message, state : FSMContext) -> None:

    if message.from_user is None:
        return

    if message.text is None:

        await message.answer("Введите сумму числом")

        return

    try:

        amount = Decimal(message.text.strip().replace(",","."))

    except InvalidOperation:

        await message.answer("Некорректная сумма")

        return

    if not amount.is_finite():

        await message.answer("Сумма должна быть конечным числом")

        return

    if amount <= 0:

        await message.answer("Сумма должна быть больше нуля")

        return

    await state.update_data(amount = amount)

    await state.set_state(CreateIncome.category)

    await message.answer(
        "Введите категорию дохода\n"
        "Например: Зарплата, Фриланс, Подарок",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateExpense.amount)
async def expense_amount(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    if message.text is None:

        await message.answer(
            "Введите сумму числом"
        )

        return

    try:

        amount = Decimal(message.text.strip().replace(",","."))

    except InvalidOperation:

        await message.answer(
            "Некорректная сумма"
        )

        return

    if not amount.is_finite():

        await message.answer(
            "Сумма должна быть конечным числом"
        )

        return

    if amount <= 0:

        await message.answer(
            "Сумма должна быть больше нуля"
        )

        return

    await state.update_data(amount = amount)

    await state.set_state(CreateExpense.category)

    await message.answer(
        "Введите категорию расхода\n"
        "Например: Продукты, Бензин, Долг",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateIncome.category)
async def income_category(message : Message, state : FSMContext) -> None:

    if message.from_user is None:
        return

    if message.text is None:

        await message.answer("Введите категорию текстом")

        return

    category = message.text.strip()

    if not category:

        await message.answer("Категория не может быть пустой")

        return

    await state.update_data(category = category)

    await state.set_state(CreateIncome.comment)

    await message.answer(
        "Введите комментарий к операции",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateExpense.category)
async def expense_category(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    if message.text is None:

        await message.answer(
            "Введите категорию текстом"
        )

        return

    category = message.text.strip()

    if not category:

        await message.answer(
            "Категория не может быть пустой"
        )

        return

    await state.update_data(category = category)

    await state.set_state(CreateExpense.comment)

    await message.answer(
        "Введите комментарий к операции",
        reply_markup= fsm_navigation_keyboard
    )

@router.message(CreateIncome.comment)
async def income_comment(message : Message, state : FSMContext) -> None:

    if message.text is None:

        await message.answer("Введите комментарий текстом")

        return

    comment = message.text.strip()

    if not comment:

        await message.answer("Комментарий не должен быть пустым")

        return

    await state.update_data(comment = comment)

    data = await state.get_data()

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

    account = account_repository.get_account_by_id(data["account_id"], user.user_id)

    if account is None:

        await state.clear()

        await message.answer(
            "Счёт больше не найден",
            reply_markup= main_keyboard
        )

        return

    if not account.is_active:

        await state.clear()

        await message.answer(
            "Счёт деактивирован",
            reply_markup= main_keyboard
        )

        return

    await state.set_state(CreateIncome.confirm)

    await message.answer(
        "Проверьте данные операции\n\n"
        "Операция: Доход\n"
        f"Счёт: {account.source}\n"
        f"Сумма: {data["amount"]} {account.currency}\n"
        f"Категория: {data["category"]}\n"
        f"Комментарий: {data["comment"]}",
        reply_markup= operation_confirm_keyboard
    )

@router.message(CreateExpense.comment)
async def expense_comment(message : Message, state : FSMContext) -> None:

    if message.text is None:

        await message.answer(
            "Введите комментарий текстом"
        )

        return

    comment = message.text.strip()

    if not comment:

        await message.answer(
            "Комментарий не должен быть пустым"
        )

        return

    await state.update_data(comment = comment)

    data = await state.get_data()

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

    account = account_repository.get_account_by_id(data["account_id"], user.user_id)

    if account is None:

        await state.clear()

        await message.answer(
            "Счёт больше не найден",
            reply_markup= main_keyboard
        )

        return

    if not account.is_active:

        await state.clear()

        await message.answer(
            "Счёт деактивирован",
            reply_markup= main_keyboard
        )

        return

    await state.set_state(CreateExpense.confirm)
    
    await message.answer(
        "Проверьте данные операции\n\n"
        "Операция: Расход\n"
        f"Счёт: {account.source}\n"
        f"Сумма: {data["amount"]} {account.currency}\n"
        f"Категория: {data["category"]}\n"
        f"Комментарий: {data["comment"]}",
        reply_markup= operation_confirm_keyboard
    )

@router.message(CreateIncome.confirm, F.text == "✅ Подтвердить операцию")
async def income_confirm(message : Message, state : FSMContext) -> None:

    if message.from_user is None:
        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден!", 
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован!",
            reply_markup= main_keyboard
        )

        return

    data = await state.get_data()

    account = account_repository.get_account_by_id(data["account_id"], user.user_id)

    if account is None:

        await state.clear()

        await message.answer(
            "Счёт не найден",
            reply_markup= main_keyboard
        )

        return

    if not account.is_active:

        await state.clear()

        await message.answer(
            "Счёт деактивирован",
            reply_markup= main_keyboard
        )

        return

    try:

        transaction = Transaction(
            action_date= date.today(),
            amount= data["amount"],
            operation= OperationType.INCOME,
            category= data["category"],
            account= account,
            comment= data["comment"],
            transaction_id= None,
            transfer_id= None,
            is_active= True
        )

        transaction_service.execute_transaction(transaction, user.user_id)

    except (ValueError, TypeError) as error:

        await message.answer(
            "Не удалось добавить доход!\n"
            f"{error}",
            reply_markup= operation_confirm_keyboard
        )

        return

    await state.clear()

    await message.answer(
        "Доход был успешно добавлен\n\n"
        f"Стал богаче на: +{transaction.amount} {account.currency}\n\n"
        f"Текущий остаток: {account.balance} {account.currency}",
        reply_markup= main_keyboard
    )

@router.message(CreateExpense.confirm, F.text == "✅ Подтвердить операцию")
async def expense_confirm(message : Message, state : FSMContext) -> None:

    if message.from_user is None:

        return

    telegram_user_id = message.from_user.id

    user = user_repository.get_user_by_telegram_id(telegram_user_id)

    if user is None:

        await state.clear()

        await message.answer(
            "Пользователь не найден!", 
            reply_markup= main_keyboard
        )

        return

    if not user.is_active:

        await state.clear()

        await message.answer(
            "Пользователь деактивирован!",
            reply_markup= main_keyboard
        )

        return

    data = await state.get_data()

    account = account_repository.get_account_by_id(data["account_id"], user.user_id)

    if account is None:

        await state.clear()

        await message.answer(
            "Счёт не найден",
            reply_markup= main_keyboard
        )

        return

    if not account.is_active:

        await state.clear()

        await message.answer(
            "Счёт деактивирован",
            reply_markup= main_keyboard
        )

        return

    try:

        transaction = Transaction(
            action_date= date.today(),
            amount= data["amount"],
            operation= OperationType.EXPENSE,
            category= data["category"],
            account= account,
            comment= data["comment"],
            transaction_id= None,
            transfer_id= None,
            is_active= True
        )

        transaction_service.execute_transaction(transaction, user.user_id)

    except (ValueError, TypeError) as error:

        await message.answer(
            "Не удалось добавить расход!\n"
            f"{error}",
            reply_markup= operation_confirm_keyboard
        )
        
        return
        
    await state.clear()
        
    await message.answer(
        "Расход был успешно добавлен\n\n"
        f"Победнел на: -{transaction.amount} {account.currency}\n\n"
        f"Текущий остаток: {account.balance} {account.currency}",
        reply_markup= main_keyboard
    )

@router.message(CreateIncome.confirm)
async def invalid_income_confirm(message : Message) -> None:

    await message.answer(
        "Подтвердите информацию с помощью кнопки",
        reply_markup= operation_confirm_keyboard
    )

@router.message(CreateExpense.confirm)
async def invalid_expense_confirm(message : Message) -> None:

    await message.answer(
        "Подтвердите информацию с помощью кнопки",
        reply_markup= operation_confirm_keyboard
    )