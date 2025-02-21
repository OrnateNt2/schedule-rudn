from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import (
    set_user_group,
    set_user_notification_time,
    set_user_program,
    set_user_language,
    get_user_group,
    get_user_program,
    get_user_notification_time,
    get_user_course,
    set_user_course
)
from services.cache import get_all_groups, get_available_languages
import math

PROGRAM_OPTIONS = ["ФГОС", "МП"]
NOTIFICATION_TIMES = ["07:00", "08:00", "09:00", "10:00", "20:00"]
GROUPS_PER_PAGE = 6  # Количество групп на странице

def generate_group_keyboard(groups, current_page=0, current_group=None):
    total_pages = math.ceil(len(groups) / GROUPS_PER_PAGE)
    start_index = current_page * GROUPS_PER_PAGE
    end_index = start_index + GROUPS_PER_PAGE
    page_groups = groups[start_index:end_index]
    
    keyboard = []
    row = []
    for group in page_groups:
        button_text = f"✅ {group}" if group == current_group else group
        row.append(InlineKeyboardButton(button_text, callback_data=f"set_group:{group}:{current_page}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
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
    current_course = get_user_course(user_id)
    current_group = get_user_group(user_id)
    current_program = get_user_program(user_id)
    current_time = get_user_notification_time(user_id)
    
    # Строка для выбора курса (1-6)
    course_buttons = [
        InlineKeyboardButton(text=("✅ " + c) if current_course == c else c, callback_data=f"set_course:{c}")
        for c in ["1", "2", "3", "4", "5", "6"]
    ]
    
    # Получаем список групп из расписания для выбранного курса, если установлен
    groups = get_all_groups(current_course) if current_course else []
    group_keyboard = generate_group_keyboard(groups, current_page=0, current_group=current_group)
    
    time_buttons = [
        InlineKeyboardButton(text=("✅ " + t) if current_time == t else t, callback_data=f"set_time:{t}")
        for t in NOTIFICATION_TIMES
    ]
    program_buttons = [
        InlineKeyboardButton(text=("✅ " + p) if current_program == p else p, callback_data=f"set_program:{p}")
        for p in PROGRAM_OPTIONS
    ]
    
    keyboard = [
        [InlineKeyboardButton("Выберите курс:", callback_data="ignore")],
        course_buttons,
        [InlineKeyboardButton("Выберите группу:", callback_data="ignore")],
        *group_keyboard.inline_keyboard,
        time_buttons,
        program_buttons,
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Настройки:\nВыберите курс, группу, время оповещений и программу (ФГОС/МП):",
        reply_markup=reply_markup
    )

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":", 1)
    action = data[0]
    value = data[1]
    response = ""
    
    if action == "set_group":
        # Формат: set_group:{group}:{page}
        parts = query.data.split(":")
        group = parts[1]
        set_user_group(query.from_user.id, group)
        response = f"Группа установлена: {group}"
    elif action == "group_page":
        new_page = int(value)
        current_course = get_user_course(query.from_user.id)
        groups = get_all_groups(current_course) if current_course else []
        current_group = get_user_group(query.from_user.id)
        group_keyboard = generate_group_keyboard(groups, current_page=new_page, current_group=current_group)
        current_program = get_user_program(query.from_user.id)
        current_time = get_user_notification_time(query.from_user.id)
        program_buttons = [
            InlineKeyboardButton(text=("✅ " + p) if current_program == p else p, callback_data=f"set_program:{p}")
            for p in PROGRAM_OPTIONS
        ]
        time_buttons = [
            InlineKeyboardButton(text=("✅ " + t) if current_time == t else t, callback_data=f"set_time:{t}")
            for t in NOTIFICATION_TIMES
        ]
        course_buttons = [
            InlineKeyboardButton(text=("✅ " + c) if get_user_course(query.from_user.id) == c else c, callback_data=f"set_course:{c}")
            for c in ["1", "2", "3", "4", "5", "6"]
        ]
        keyboard = [
            [InlineKeyboardButton("Выберите курс:", callback_data="ignore")],
            course_buttons,
            [InlineKeyboardButton("Выберите группу:", callback_data="ignore")],
            *group_keyboard.inline_keyboard,
            time_buttons,
            program_buttons,
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        return
    elif action == "set_time":
        set_user_notification_time(query.from_user.id, value)
        response = f"Время оповещений установлено: {value}"
    elif action == "set_program":
        set_user_program(query.from_user.id, value)
        response = f"Программа установлена: {value}"
        group = get_user_group(query.from_user.id)
        current_course = get_user_course(query.from_user.id)
        if group:
            langs = get_available_languages(group, current_course, program=value)
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
        set_user_language(query.from_user.id, value)
        response = f"Язык установлен: {value}"
    elif action == "set_course":
        # Обработчик для выбора курса в настройках
        set_user_course(query.from_user.id, value)
        response = f"Курс установлен: {value}"
    
    # Перестраиваем клавиатуру с обновленными настройками
    user_id = query.from_user.id
    current_course = get_user_course(user_id)
    course_buttons = [
        InlineKeyboardButton(text=("✅ " + c) if current_course == c else c, callback_data=f"set_course:{c}")
        for c in ["1", "2", "3", "4", "5", "6"]
    ]
    groups = get_all_groups(current_course) if current_course else []
    group_keyboard = generate_group_keyboard(groups, current_page=0, current_group=get_user_group(user_id))
    current_program = get_user_program(user_id)
    current_time = get_user_notification_time(user_id)
    time_buttons = [
        InlineKeyboardButton(text=("✅ " + t) if current_time == t else t, callback_data=f"set_time:{t}")
        for t in NOTIFICATION_TIMES
    ]
    program_buttons = [
        InlineKeyboardButton(text=("✅ " + p) if current_program == p else p, callback_data=f"set_program:{p}")
        for p in PROGRAM_OPTIONS
    ]
    keyboard = [
        [InlineKeyboardButton("Выберите курс:", callback_data="ignore")],
        course_buttons,
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
    pattern="^(set_group|group_page|set_time|set_program|set_language|set_course):"
)
