from transaction import Transaction
from database import get_connection
from money import to_minor_units

class TransactionRepository:
    """Описание работы с таблицей transactions"""

    def add_transactions(self, transaction : Transaction) -> int:
        """Функция добавляет в таблицу transactions новую транзакцию"""

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is not None:
            raise ValueError("Данная транзакция уже имеет идетнификатор")

        if transaction.account.object_number is None:
            raise ValueError("Счёт транзакции сначала должен быть сохранен в базе")

        amount_minor = to_minor_units(transaction.amount)

        conection = get_connection()

        try:

            cursor = conection.execute(
                """
                INSERT INTO transactions (
                    action_date,
                    amount_minor,
                    operation,
                    category,
                    acount_id,
                    comment,
                    is_active
                )
                VALUES (?,?,?,?,?,?,?)
                """,
                transaction.action_date.isoformat(),
                amount_minor,
                transaction.operation.value,
                transaction.category,
                transaction.account.object_number,
                transaction.comment,
                int(transaction.is_active),
            )

            conection.commit()

            transaction.transaction_id = cursor.lastrowid

            return transaction.transaction_id

        except Exception:
            conection.rollback()
            raise

        finally:
            conection.close()