# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN', 'YOUR_DEFAULT_TOKEN')
# CURRENT_WEEK_PARITY = "even" означает: если номер недели чётный → верхняя, иначе нижняя.
# Если "odd", то наоборот.
CURRENT_WEEK_PARITY = os.getenv('CURRENT_WEEK_PARITY', 'even').lower()
