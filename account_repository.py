from account import Account
from database import get_connection
from money import to_minor_units, from_minor_units

class AccountRepository:
    """Описание работы с таблицей accounts"""

    def add_account(self, account : Account) -> int:
        """Функция добавляет новый счёт в базу"""

        if not isinstance(account, Account):
            raise TypeError("Должен быть передан объект Account")

        if account.object_number is not None:
            raise ValueError("Этот счёт уже имеет идентификатор")

        balance_minor = to_minor_units(account.balance)

        limit_minor = (
            to_minor_units(account.limit)
            if account.limit is not None
            else None
            )

        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO accounts (
                    source,
                    acc_type,
                    product_name,
                    requisites,
                    currency,
                    balance_minor,
                    limit_minor,
                    is_active
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    account.source,
                    account.acc_type,
                    account.product_name,
                    account.requisites,
                    account.currency,
                    balance_minor,
                    limit_minor,
                    int(account.is_active),
                )
            )

            connection.commit()

            account.object_number = cursor.lastrowid

            return account.object_number


        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_account_by_id(self, account_id : int) -> Account | None:
        """Восстанавливает объект Account по прочитаной строке SQL"""

        if type(account_id) is not int:
            raise TypeError("Идентификатор счёта должен быть целочисленного типа")

        if account_id <= 0:
            raise ValueError("Идентификатор счёта должен быть больше нуля")

        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    id,
                    source,
                    acc_type,
                    product_name,
                    requisites,
                    currency,
                    balance_minor,
                    limit_minor,
                    is_active
                FROM accounts
                WHERE id = ?
                """,
                (account_id,),
            ).fetchone()

        finally:

            connection.close()

        if row is None:
            return None

        return Account(
            object_number = row["id"],
            source = row["source"],
            acc_type = row["acc_type"],
            product_name = row["product_name"],
            requisites = row["requisites"],
            balance = from_minor_units(row["balance_minor"]),
            currency = row["currency"],
            limit = (from_minor_units(row["limit_minor"]) 
                     if row["limit_minor"] is not None 
                     else None
            ),
            is_active = bool(row["is_active"])
        )

    def get_all_accounts(self) -> list[Account]:
        """Возвращает список всех аккаунтов добавленных в базу"""

        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    source,
                    acc_type,
                    product_name,
                    requisites,
                    currency,
                    balance_minor,
                    limit_minor,
                    is_active
                FROM accounts
                ORDER BY id
                """
            ).fetchall()

        finally:
            connection.close()

        accounts = []

        for row in rows:

            account = Account(
            object_number = row["id"],
            source = row["source"],
            acc_type = row["acc_type"],
            product_name = row["product_name"],
            requisites = row["requisites"],
            balance = from_minor_units(row["balance_minor"]),
            currency = row["currency"],
            limit = (from_minor_units(row["limit_minor"]) 
                     if row["limit_minor"] is not None 
                     else None
            ),
            is_active = bool(row["is_active"])
            )

            accounts.append(account)

        return accounts

    def get_active_accounts(self) -> list[Account]:
        """Возвращает список всех активных аккаунтов добавленных в базу"""

        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    source,
                    acc_type,
                    product_name,
                    requisites,
                    currency,
                    balance_minor,
                    limit_minor,
                    is_active
                FROM accounts
                WHERE is_active = 1
                ORDER BY id
                """
            ).fetchall()

        finally:
            connection.close()

        accounts = []

        for row in rows:

            account = Account(
            object_number = row["id"],
            source = row["source"],
            acc_type = row["acc_type"],
            product_name = row["product_name"],
            requisites = row["requisites"],
            balance = from_minor_units(row["balance_minor"]),
            currency = row["currency"],
            limit = (from_minor_units(row["limit_minor"]) 
                     if row["limit_minor"] is not None 
                     else None
            ),
            is_active = bool(row["is_active"])
            )

            accounts.append(account)

        return accounts

    def delete_account_by_id(self, account_id : int) -> None:
        """
        Функция удаляет случайные или неправильные записи из таблицы
        Применяется только для случайных записей без финансовой истории
        """

        if type(account_id) is not int:
            raise TypeError("Идентификатор счёта должен быть целочисленного типа")

        if account_id <= 0:
            raise ValueError("Идентификатор счёта должен быть больше нуля")

        connection = get_connection()

        try:
            cursor = connection.execute(
                    """
                    DELETE FROM accounts
                    WHERE id = ?
                    """,
                    (account_id,)
                )

            if cursor.rowcount == 0:

                raise ValueError("Записи с таким идентификатором не существует")
        
            connection.commit()

        except Exception:

            connection.rollback()
            raise

        finally:

            connection.close()

    def update_account(self, account : Account) -> None:
        """Функция обнавляет данные существующей записи в таблице"""

        if not isinstance(account, Account):
            raise TypeError("Должен быть передан объект акаунт")

        if account.object_number is None:
            raise ValueError("Нельзя обновить счёт без идентификатора")

        balance_minor = to_minor_units(account.balance)

        limit_minor = (
            to_minor_units(account.limit)
            if account.limit is not None
            else None
                       )

        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                UPDATE accounts
                SET
                    source = ?,
                    acc_type = ?,
                    product_name = ?,
                    requisites = ?,
                    currency = ?,
                    balance_minor =?,
                    limit_minor = ?,
                    is_active = ?
                WHERE id = ?
                """,
                (
                    account.source,
                    account.acc_type,
                    account.product_name,
                    account.requisites,
                    account.currency,
                    balance_minor,
                    limit_minor,
                    int(account.is_active),
                    account.object_number,
                 )
            )

            if cursor.rowcount == 0:
                raise ValueError("Записи с таким идентификатором не существует")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()