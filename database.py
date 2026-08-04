import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "finance.db"

def get_connection() -> sqlite3.Connection:
    """Создает подключение к базе данных и возвращает его в виде объекта"""

    connection = sqlite3.Connection(DB_PATH)

    # Позволяет получать значения столбцов по их названию
    connection.row_factory = sqlite3.Row

    # Включает контроль внешних ключей в SQLite.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

def create_tables() -> None:
    """Создаёт необходимые таблицы, если они ещё не существуют."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source TEXT NOT NULL,
                acc_type TEXT NOT NULL,
                product_name TEXT,
                requisites TEXT,
                currency TEXT NOT NULL,
                
                balance_minor INTEGER NOT NULL DEFAULT 1,
                limit_minor INTEGER,

                is_active INTEGER
            )
            """
        )