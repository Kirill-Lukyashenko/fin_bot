from transaction import Transaction
from database import get_connection
from money import to_minor_units

class TransactionRepository:
    """Описание работы с таблицей transactions"""

    def add_transaction(self, transaction : Transaction) -> int:
        """Функция добавляет в таблицу transactions новую транзакцию"""

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is not None:
            raise ValueError("Данная транзакция уже имеет идетнификатор")

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