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
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL UNIQUE,
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN(0,1))
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,

                source TEXT NOT NULL,
                acc_type TEXT NOT NULL,
                product_name TEXT,
                requisites TEXT,
                currency TEXT NOT NULL,
                
                balance_minor INTEGER NOT NULL DEFAULT 0
                    CHECK(balance_minor >=0),
                limit_minor INTEGER,

                is_active INTEGER NOT  NULL DEFAULT 1 CHECK (is_active IN(0,1)),

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE RESTRICT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN (0, 1))
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
            
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                action_date TEXT NOT NULL,
                amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),

                operation TEXT NOT NULL CHECK (
                    (
                        operation IN ('Доход', 'Расход') 
                        AND transfer_id is NULL
                    ) 
                    OR 
                    (
                        operation IN ('Перевод входящий','Перевод исходящий') 
                        AND transfer_id IS NOT NULL
                    )
                ),

                category TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                comment TEXT NOT NULL,

                is_active INTEGER NOT  NULL DEFAULT 1 CHECK (is_active IN(0,1)),

                transfer_id INTEGER,

                FOREIGN KEY (account_id)
                    REFERENCES accounts(id)
                    ON DELETE RESTRICT,

                FOREIGN KEY (transfer_id)
                    REFERENCES transfers(id)
                    ON DELETE RESTRICT
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS 
                idx_accounts_user_id
            ON accounts(user_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_transactions_action_date_id
            ON transactions(action_date,id)
            """
        )
