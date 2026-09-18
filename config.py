import os

from dotenv import load_dotenv

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise RuntimeError("Переменная BOT_TOKEN не найдена .env")

DB_NAME = os.getenv("DB_NAME")

if DB_NAME is None:
    raise RuntimeError("Переменная DB_NAME не найдена в .env")

DB_PATH = BASE_DIR / DB_NAME