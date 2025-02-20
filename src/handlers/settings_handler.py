# src/handlers/settings_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import (
    set_user_group, set_user_notification_time,
    set_user_program, set_user_language,
    get_user_group, get_user_program
)
from services.cache import get_all_groups, get_available_languages
import math

PROGRAM_OPTIONS = ["ФГОС", "МП"]
NOTIFICATION_TIMES = ["07:00", "08:00", "09:00", "10:00"]
GROUPS_PER_PAGE = 6  # Количество групп на одной странице

def generate_group_keyboard(groups, current_page=0, current_group=None):
    """
    Создаёт inline-клавиатуру для выбора группы с пагинацией.
    Каждая кнопка имеет callback_data вида:
      - group_select:{group}:{current_page}
    Навигационные кнопки имеют callback_data:
      - group_page:{new_page}
    """
    total_pages = math.ceil(len(groups) / GROUPS_PER_PAGE)
    start_index = current_page * GROUPS_PER_PAGE
    end_index = start_index + GROUPS_PER_PAGE
    page_groups = groups[start_index:end_index]
    
    keyboard = []
    row = []
    # Располагаем по 2 кнопки в строке
    for group in page_groups:
        button_text = f"✅ {group}" if group == current_group else group
        row.append(InlineKeyboardButton(button_text, callback_data=f"group_select:{group}:{current_page}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Добавляем навигацию, если страниц больше одной
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("← Предыдущая", callback_data=f"group_page:{current_page-1}"))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Следующая →", callback_data=f"group_page:{current_page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_group = get_user_group(user_id)
    current_program = get_user_program(user_id)
    
    groups = get_all_groups()
    if not groups:
        await update.message.reply_text("Не удалось загрузить группы из расписания.")
        return

    # Создаём клавиатуру для выбора группы с пагинацией (начинаем с первой страницы)
    group_keyboard = generate_group_keyboard(groups, current_page=0, current_group=current_group)
    
    # Остальные кнопки (время и программа) остаются без изменений
    time_buttons = [
        InlineKeyboardButton(text=t, callback_data=f"set_time:{t}")
        for t in NOTIFICATION_TIMES
    ]
    program_buttons = [
        InlineKeyboardButton(
            text=("✅ " + p) if current_program == p else p,
            callback_data=f"set_program:{p}"
        )
        for p in PROGRAM_OPTIONS
    ]
    
    # Собираем итоговую клавиатуру
    keyboard = [
        [InlineKeyboardButton("Выберите группу:", callback_data="ignore")],  # Заголовок
        *group_keyboard.inline_keyboard,
        time_buttons,
        program_buttons,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Настройки:\nВыберите группу, время уведомлений и программу (ФГОС/МП):",
        reply_markup=reply_markup
    )

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":", 2)
    action = data[0]
    
    if action == "group_select":
        # Формат callback_data: group_select:{group}:{current_page}
        group = data[1]
        current_page = int(data[2]) if len(data) > 2 else 0
        set_user_group(query.from_user.id, group)
        response = f"Группа установлена: {group}"
        # Обновляем клавиатуру с отметкой выбранной группы
        groups = get_all_groups()
        group_keyboard = generate_group_keyboard(groups, current_page=current_page, current_group=group)
        current_program = get_user_program(query.from_user.id)
        time_buttons = [InlineKeyboardButton(text=t, callback_data=f"set_time:{t}") for t in NOTIFICATION_TIMES]
        program_buttons = [
            InlineKeyboardButton(text=("✅ " + p) if current_program == p else p, callback_data=f"set_program:{p}")
            for p in PROGRAM_OPTIONS
        ]
        keyboard = [
            [InlineKeyboardButton("Выберите группу:", callback_data="ignore")],
            *group_keyboard.inline_keyboard,
            time_buttons,
            program_buttons,
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(response, reply_markup=reply_markup)
        return
    elif action == "group_page":
        # Формат: group_page:{new_page}
        new_page = int(data[1])
        groups = get_all_groups()
        current_group = get_user_group(query.from_user.id)
        group_keyboard = generate_group_keyboard(groups, current_page=new_page, current_group=current_group)
        current_program = get_user_program(query.from_user.id)
        time_buttons = [InlineKeyboardButton(text=t, callback_data=f"set_time:{t}") for t in NOTIFICATION_TIMES]
        program_buttons = [
            InlineKeyboardButton(text=("✅ " + p) if current_program == p else p, callback_data=f"set_program:{p}")
            for p in PROGRAM_OPTIONS
        ]
        keyboard = [
            [InlineKeyboardButton("Выберите группу:", callback_data="ignore")],
            *group_keyboard.inline_keyboard,
            time_buttons,
            program_buttons,
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        return
    elif action == "set_time":
        value = data[1]
        set_user_notification_time(query.from_user.id, value)
        response = f"Время уведомлений установлено: {value}"
    elif action == "set_program":
        value = data[1]
        set_user_program(query.from_user.id, value)
        response = f"Программа установлена: {value}"
        group = get_user_group(query.from_user.id)
        if group:
            langs = get_available_languages(group, program=value)
            if langs:
                if len(langs) == 1:
                    set_user_language(query.from_user.id, langs[0])
                    response += f"\nЯзык установлен автоматически: {langs[0]}"
                else:
                    lang_buttons = [InlineKeyboardButton(text=lang, callback_data=f"set_language:{lang}") for lang in langs]
                    reply_markup = InlineKeyboardMarkup([[btn] for btn in lang_buttons])
                    response += "\nВыберите язык:"
                    await query.edit_message_text(response, reply_markup=reply_markup)
                    return
            else:
                response += "\nДоступных вариантов языка не найдено."
    elif action == "set_language":
        value = data[1]
        set_user_language(query.from_user.id, value)
        response = f"Язык установлен: {value}"
    
    # Перестраиваем клавиатуру с обновлёнными значениями
    user_id = query.from_user.id
    current_group = get_user_group(user_id)
    groups = get_all_groups()
    group_keyboard = generate_group_keyboard(groups, current_page=0, current_group=current_group)
    current_program = get_user_program(user_id)
    time_buttons = [InlineKeyboardButton(text=t, callback_data=f"set_time:{t}") for t in NOTIFICATION_TIMES]
    program_buttons = [
        InlineKeyboardButton(text=("✅ " + p) if current_program == p else p, callback_data=f"set_program:{p}")
        for p in PROGRAM_OPTIONS
    ]
    keyboard = [
        [InlineKeyboardButton("Выберите группу:", callback_data="ignore")],
        *group_keyboard.inline_keyboard,
        time_buttons,
        program_buttons,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup)

settings_handler = CommandHandler("settings", settings_command)
settings_callback_handler = CallbackQueryHandler(
    settings_callback,
    pattern="^(group_select|group_page|set_time|set_program|set_language):"
)
