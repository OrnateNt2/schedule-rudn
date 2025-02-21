import os
import json

DB_PATH = os.path.join("data", "users.json")

def load_users():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_user_if_not_exists(user_id):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        users[str_user_id] = {
            "course": None,
            "group": None,
            "notification_time": None,
            "subscribed": False,
            "program": None,
            "language": None
        }
        save_users(users)

def get_user_course(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("course")

def set_user_course(user_id, course):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        add_user_if_not_exists(user_id)
        users = load_users()
    users[str_user_id]["course"] = course
    save_users(users)

def get_user_group(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("group")

def set_user_group(user_id, group):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        add_user_if_not_exists(user_id)
        users = load_users()
    users[str_user_id]["group"] = group
    save_users(users)

def get_user_notification_time(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("notification_time")

def set_user_notification_time(user_id, time_str):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        add_user_if_not_exists(user_id)
        users = load_users()
    users[str_user_id]["notification_time"] = time_str
    save_users(users)

def get_user_subscribe_status(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("subscribed")

def set_user_subscribe_status(user_id, status: bool):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        add_user_if_not_exists(user_id)
        users = load_users()
    users[str_user_id]["subscribed"] = status
    save_users(users)

def get_user_program(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("program")

def set_user_program(user_id, program):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        add_user_if_not_exists(user_id)
        users = load_users()
    users[str_user_id]["program"] = program
    save_users(users)

def get_user_language(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("language")

def set_user_language(user_id, language):
    users = load_users()
    str_user_id = str(user_id)
    if str_user_id not in users:
        add_user_if_not_exists(user_id)
        users = load_users()
    users[str_user_id]["language"] = language
    save_users(users)
