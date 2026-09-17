from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def accounts_select_keyboard(accounts) -> ReplyKeyboardMarkup:

    builder = ReplyKeyboardBuilder()

    for account in accounts:

        if account.product_name is not None:

            button_text = f"{account.source}\n{account.product_name}"

        else:

            button_text = account.source

        builder.add(
            KeyboardButton(text=button_text)
        )

    if len(accounts) <= 4:
        builder.adjust(1)
    else:
        builder.adjust(2)

    builder.row(
        KeyboardButton(text="❌ Отмена")
    )

    return builder.as_markup(
        resize_keyboard=True
    )

main_keyboard = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text= "💰 Счета")
        ],
        [
            KeyboardButton(text= "📥 Доход"),
            KeyboardButton(text= "📤 Расход")
        ],
        [
            KeyboardButton(text= "♻️ Перевод"),
            KeyboardButton(text= "📖 История")
        ],
        [
            KeyboardButton(text= "📊 Статистика"),
            KeyboardButton(text= "⚙️ Настройки")
        ],
    ],
    resize_keyboard= True
)

accounts_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= "Создать счёт")
        ],
        [
            KeyboardButton(text= "Получить список счетов"),
            KeyboardButton(text= "Получить счёт по идентификатору")
        ],
        [
            KeyboardButton(text= "В главное меню")
        ],
    ],
    resize_keyboard=  True
)

fsm_navigation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= "⬅️ Назад")
        ],
        [
            KeyboardButton(text= "❌ Отмена")
        ],
    ],
    resize_keyboard= True
)

account_confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= "✅ Создать счёт")
        ],
        [
            KeyboardButton(text= "⬅️ Назад"),
            KeyboardButton(text= "❌ Отмена")
        ],
    ],
    resize_keyboard= True
)

operation_confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= "✅ Подтвердить операцию")
        ],
        [
            KeyboardButton(text= "⬅️ Назад"),
            KeyboardButton(text= "❌ Отмена")
        ],
    ],
    resize_keyboard= True
)

transfer_confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= "✅ Подтвердить перевод")
        ],
        [
            KeyboardButton(text= "⬅️ Назад"),
            KeyboardButton(text= "❌ Отмена")
        ],
    ],
    resize_keyboard= True
)

statistics_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сумма на всех счетах"),
            KeyboardButton(text="Расходы за сегодня"),
        ],
        [
            KeyboardButton(text="Расходы за текущую неделю"),
            KeyboardButton(text="Расходы за текущий месяц")
        ],
        [
            KeyboardButton(text="Главное меню")
        ],
    ],
    resize_keyboard= True
)