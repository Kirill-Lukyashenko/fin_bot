from transaction import Transaction, OperationType
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
