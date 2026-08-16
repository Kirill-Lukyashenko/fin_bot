from transaction import Transaction, OperationType
from account import Account
from database import get_connection
from money import to_minor_units, from_minor_units
from datetime import date
from account_repository import AccountRepository

class TransactionRepository:
    """Описание работы с таблицей transactions"""

    def add_transaction(self, transaction : Transaction) -> int:
        """Функция добавляет в таблицу transactions новую транзакцию"""

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is not None:
            raise ValueError("Данная транзакция уже имеет идентификатор")

        if transaction.account.object_number is None:
            raise ValueError("Счёт транзакции сначала должен быть сохранен в базе")

        amount_minor = to_minor_units(transaction.amount)

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
                    is_active
                )
                VALUES (?,?,?,?,?,?,?)
                """,
                (transaction.action_date.isoformat(),
                amount_minor,
                transaction.operation.value,
                transaction.category,
                transaction.account.object_number,
                transaction.comment,
                int(transaction.is_active))
            )

            connection.commit()

            transaction.transaction_id = cursor.lastrowid

            return transaction.transaction_id

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def delete_transaction_by_id(self,transaction_id :int) -> None:
        """Функция удаляет транзакцию из базы данных"""

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
                """,
                (transaction_id,)
            )

            if cursor.rowcount == 0:

                raise ValueError("Транзакции с таким id не существует")

            connection.commit()


        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def update_transaction(self, transaction: Transaction) -> None:
        """Функция обновляет данные существующей транзакции в таблице"""

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is None:
            raise ValueError("Нельзя обновить транзакцию не имеющую идентификатора")

        if transaction.account.object_number is None:
            raise ValueError("Счёт транзакции должен быть сохранён в базе")

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
                    is_active = ?
                WHERE id = ?
                """,
                (
                    transaction.action_date.isoformat(),
                    amount_minor,
                    transaction.operation.value,
                    transaction.category,
                    transaction.account.object_number,
                    transaction.comment,
                    int(transaction.is_active),
                    transaction.transaction_id
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


    def get_transaction_by_id(self, transaction_id : int) -> Transaction:
        """Функция восстанавливает объект Transaction по идентификатору"""

        if type(transaction_id) is not int:
            raise TypeError("Передаваемый идентификатор должен быть целочисленным")

        if transaction_id <= 0:
            raise ValueError("Передаваемый идентификатор должен быть больше нуля")

        connection = get_connection()

        try:

            transaction_row = connection.execute(
                """
                SELECT
                    id,
                    action_date,
                    amount_minor,
                    operation,
                    category,
                    account_id,
                    comment,
                    is_active
                FROM transactions
                WHERE id = ?
                """,
                (transaction_id,)
            ).fetchone()

            if transaction_row is None:
                raise ValueError("Не существует транзакции с таким идентификатором")

        finally:

            connection.close()

        account_repository = AccountRepository()

        account = account_repository.get_account_by_id(transaction_row["account_id"])

        if account is None:
            raise ValueError("Счёта с указанным идентификатором не существует")

        amount = from_minor_units(transaction_row["amount_minor"])

        return Transaction(
                action_date= date.fromisoformat(transaction_row["action_date"]),
                amount= amount,
                operation= OperationType(transaction_row["operation"]),
                category= transaction_row["category"],
                account= account,
                comment= transaction_row["comment"],
                transaction_id= transaction_row["id"],
                is_active= bool(transaction_row["is_active"])
            )

    def get_transactions_by_period(self, date_start: date, date_end: date, limit : int = 50, offset : int = 0) -> list[Transaction]:
        """Функция возвращает список транзакций за временной период"""

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
                    t.is_active AS transaction_is_active,

                    a.id AS account_id,
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

                ORDER BY
                    t.action_date DESC,
                    t.id DESC

                LIMIT ?
                OFFSET ?
                """,
                (
                    date_start.isoformat(),
                    date_end.isoformat(),
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
                is_active= bool(row["transaction_is_active"])
            )

            transactions.append(transaction)

        return transactions