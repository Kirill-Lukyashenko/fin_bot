from transaction import Transaction, OperationType
from account import Account
from database import get_connection
from money import to_minor_units, from_minor_units
from datetime import date

class TransactionRepository:
    """Описание работы с таблицей transactions"""

    def add_transaction(self, transaction : Transaction, user_id : int) -> int:
        """Функция добавляет в таблицу transactions новую транзакцию"""

        if type(user_id) is not int:
            raise TypeError("Передаваемый идентификатор пользователя должен быть целочисленным")
                                
        if user_id <= 0:
            raise ValueError("Передаваемый идентификатор пользователя должен быть больше нуля")

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is not None:
            raise ValueError("Данная транзакция уже имеет идентификатор")

        if transaction.account.object_number is None:
            raise ValueError("Счёт транзакции сначала должен быть сохранен в базе")

        amount_minor = to_minor_units(transaction.amount)

        if transaction.account.user_id != user_id:
            raise ValueError("Счёт транзакции не принадлежит пользователю")

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                INSERT INTO transactions (
                    action_date,
                    amount_minor,
                    operation,
                    category,
                    account_id,
                    comment,
                    transfer_id,
                    is_active
                )
                SELECT 
                    ?,
                    ?,
                    ?,
                    ?,
                    a.id,
                    ?,
                    ?,
                    ?
                FROM accounts AS a

                WHERE a.id = ?
                AND a.user_id = ?
                
                """,
                (
                    transaction.action_date.isoformat(),
                    amount_minor,
                    transaction.operation.value,
                    transaction.category,
                    transaction.comment,
                    transaction.transfer_id,
                    int(transaction.is_active),
                    transaction.account.object_number,
                    user_id,
                )
            )

            if cursor.rowcount == 0:
                raise ValueError("Счёт не найден или не принадлежит пользователю")

            connection.commit()

            transaction.transaction_id = cursor.lastrowid

            return transaction.transaction_id

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def delete_transaction_by_id(self,transaction_id :int, user_id : int) -> None:
        """Функция удаляет транзакцию из базы данных"""

        if type(user_id) is not int:
            raise TypeError("Передаваемый идентификатор пользователя должен быть целочисленным")
                        
        if user_id <= 0:
            raise ValueError("Передаваемый идентификатор пользователя должен быть больше нуля")

        if type(transaction_id) is not int:
            raise TypeError("Идентификатор транзакции должен быть целочисленного типа")

        if transaction_id <= 0:
            raise ValueError("Идентификатор транзакции должен быть больше нуля")

        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                DELETE FROM transactions
                WHERE id = ?
                AND transfer_id IS NULL
                AND account_id IN (
                    SELECT id
                    FROM accounts
                    WHERE user_id = ?
                )
                """,
                (
                    transaction_id,
                    user_id,
                )
            )

            if cursor.rowcount == 0:

                raise ValueError("Транзакции с таким id не существует")

            connection.commit()


        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def update_transaction(self, transaction: Transaction, user_id : int) -> None:
        """Функция обновляет данные существующей транзакции в таблице"""

        if type(user_id) is not int:
            raise TypeError("Передаваемый идентификатор пользователя должен быть целочисленным")
                
        if user_id <= 0:
            raise ValueError("Передаваемый идентификатор пользователя должен быть больше нуля")

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is None:
            raise ValueError("Нельзя обновить транзакцию не имеющую идентификатора")

        if transaction.account.object_number is None:
            raise ValueError("Счёт транзакции должен быть сохранён в базе")

        if transaction.account.user_id != user_id:
            raise ValueError("Счёт транзакции не принадлежит пользователю")

        amount_minor = to_minor_units(transaction.amount)

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                UPDATE transactions
                SET
                    action_date = ?,
                    amount_minor = ?,
                    operation = ?,
                    category = ?,
                    account_id = ?,
                    comment = ?,
                    transfer_id = ?,
                    is_active = ?
                WHERE id = ?
                AND transfer_id IS NULL

                AND EXISTS (
                    SELECT 1 
                    FROM accounts AS current_account
                    WHERE current_account.id = transactions.account_id
                    AND current_account.user_id = ?
                )

                AND EXISTS (
                    SELECT 1
                    FROM accounts AS new_account
                    WHERE new_account.id = ?
                    AND new_account.user_id = ?
                )
                """,
                (
                    transaction.action_date.isoformat(),
                    amount_minor,
                    transaction.operation.value,
                    transaction.category,
                    transaction.account.object_number,
                    transaction.comment,
                    transaction.transfer_id,
                    int(transaction.is_active),
                    transaction.transaction_id,
                    user_id,
                    transaction.account.object_number,
                    user_id,
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

    def get_transaction_by_id(self, transaction_id : int, user_id : int) -> Transaction | None:
        """Функция восстанавливает объект Transaction по идентификатору"""

        if type(transaction_id) is not int:
            raise TypeError("Передаваемый идентификатор транзакции должен быть целочисленным")

        if transaction_id <= 0:
            raise ValueError("Передаваемый идентификатор транзакции должен быть больше нуля")

        if type(user_id) is not int:
            raise TypeError("Передаваемый идентификатор пользователя должен быть целочисленным")
        
        if user_id <= 0:
            raise ValueError("Передаваемый идентификатор пользователя должен быть больше нуля")

        connection = get_connection()

        try:

            row = connection.execute(
                """
                SELECT
                    t.id AS transaction_id,
                    t.action_date,
                    t.amount_minor,
                    t.operation,
                    t.category,
                    t.comment,
                    t.is_active AS transaction_is_active,
                    t.transfer_id,

                    a.id AS account_id,
                    a.user_id,
                    a.source,
                    a.acc_type,
                    a.product_name,
                    a.requisites,
                    a.currency,
                    a.balance_minor,
                    a.limit_minor,
                    a.is_active AS account_is_active
                
                FROM transactions AS t

                JOIN accounts AS a
                    ON a.id = t.account_id

                WHERE t.id = ?
                AND a.user_id = ?
                """,
                (
                    transaction_id,
                    user_id,
                )
            ).fetchone()

            if row is None:
                return None

        finally:

            connection.close()

        account = Account(
            object_number= row["account_id"],
            user_id= row["user_id"],
            source= row["source"],
            acc_type= row["acc_type"],
            product_name= row["product_name"],
            requisites= row["requisites"],
            balance= from_minor_units(row["balance_minor"]),
            currency= row["currency"],
            limit= (from_minor_units(row["limit_minor"]) if row["limit_minor"] is not None else None),
            is_active= bool(row["account_is_active"])
        )

        amount = from_minor_units(row["amount_minor"])

        return Transaction(
                action_date= date.fromisoformat(row["action_date"]),
                amount= amount,
                operation= OperationType(row["operation"]),
                category= row["category"],
                account= account,
                comment= row["comment"],
                transaction_id= row["transaction_id"],
                transfer_id= row["transfer_id"],
                is_active= bool(row["transaction_is_active"])
            )

    def get_transactions_by_period(self, user_id : int, date_start: date, date_end: date, limit : int = 50, offset : int = 0) -> list[Transaction]:
        """Функция возвращает список транзакций за временной период"""

        if type(user_id) is not int:
            raise TypeError("Передаваемый идентификатор пользователя должен быть целочисленным")
                
        if user_id <= 0:
            raise ValueError("Передаваемый идентификатор пользователя должен быть больше нуля")

        if not isinstance(date_start, date):
            raise TypeError("начальная дата должна быть объектом date")

        if not isinstance(date_end, date):
            raise TypeError("конечная дата должна быть объектом date")
        
        if date_start > date_end :
            raise ValueError("Дата начала не может быть больше даты конечной")

        if type(limit) is not int:
            raise TypeError("Лимит должен быть целочисленной переменной")

        if type(offset) is not int:
            raise TypeError("Смещение должно быть целочисленной переменной")

        if limit <= 0 :
            raise ValueError("Лимит должен быть больше нуля")

        if offset < 0 :
            raise ValueError("Смещение не может быть отрицательным")

        connection = get_connection()

        try:

            rows = connection.execute(
                """
                SELECT
                    t.id AS transaction_id,
                    t.action_date AS transaction_action_date,
                    t.amount_minor AS transaction_amount_minor,
                    t.operation AS transaction_operation,
                    t.category AS transaction_category,
                    t.comment AS transaction_comment,
                    t.transfer_id AS transaction_transfer_id,
                    t.is_active AS transaction_is_active,

                    a.id AS account_id,
                    a.user_id AS user_id,
                    a.source AS account_source,
                    a.acc_type AS account_type,
                    a.product_name AS account_product_name,
                    a.requisites AS account_requisites,
                    a.currency AS account_currency,
                    a.balance_minor AS account_balance_minor,
                    a.limit_minor AS account_limit_minor,
                    a.is_active AS account_is_active
                
                FROM transactions AS t

                JOIN accounts AS a
                    ON t.account_id = a.id

                WHERE t.action_date >= ?
                AND t.action_date <= ?
                AND a.user_id = ?

                ORDER BY
                    t.action_date DESC,
                    t.id DESC

                LIMIT ?
                OFFSET ?
                """,
                (
                    date_start.isoformat(),
                    date_end.isoformat(),
                    user_id,
                    limit,
                    offset,
                 )
            ).fetchall()
            
        finally:
            connection.close()


        transactions = []

        for row in rows:

            account = Account(
                object_number=row["account_id"],
                user_id= row["user_id"],
                source= row["account_source"],
                acc_type= row["account_type"],
                product_name= row["account_product_name"],
                requisites= row["account_requisites"],
                balance= from_minor_units(row["account_balance_minor"]),
                currency= row["account_currency"],
                limit= (from_minor_units(row["account_limit_minor"]) if row["account_limit_minor"] is not None else None),
                is_active= bool(row["account_is_active"])
            )

            transaction = Transaction(
                action_date= date.fromisoformat(row["transaction_action_date"]),
                amount= from_minor_units(row["transaction_amount_minor"]),
                operation= OperationType(row["transaction_operation"]),
                category= row["transaction_category"],
                account= account,
                comment= row["transaction_comment"],
                transaction_id= row["transaction_id"],
                transfer_id= row["transaction_transfer_id"],
                is_active= bool(row["transaction_is_active"])
            )

            transactions.append(transaction)

        return transactions