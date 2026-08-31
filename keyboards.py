from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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