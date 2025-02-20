# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN', 'YOUR_DEFAULT_TOKEN')
# Укажите, какая неделя сейчас активна: "upper" (верхняя) или "lower" (нижняя)
CURRENT_WEEK = os.getenv('CURRENT_WEEK', 'upper').lower()
