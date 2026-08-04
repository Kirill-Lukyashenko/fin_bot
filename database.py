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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
            
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                action_date TEXT NOT NULL,
                amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),

                operation TEXT NOT NULL CHECK (operation IN ('Доход', 'Расход')),

                category TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                comment TEXT NOT NULL,

                is_active INTEGER NOT  NULL DEFAULT 1 CHECK (is_active IN(0,1)),

                FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE RESTRICT
            
            )
            """
        )