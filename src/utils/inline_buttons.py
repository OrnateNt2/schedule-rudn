# src/utils/inline_buttons.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def generate_inline_keyboard(options, callback_prefix):
    """
    Пример универсальной функции для генерации Inline-кнопок.
    options: список значений
    callback_prefix: префикс для callback_data
    """
    keyboard = [
        [InlineKeyboardButton(text=o, callback_data=f"{callback_prefix}:{o}") for o in options]
    ]
    return InlineKeyboardMarkup(keyboard)
