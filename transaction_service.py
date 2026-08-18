from transaction import Transaction, OperationType
from database import get_connection
from money import to_minor_units

class TransactionService:
    """Логика поведения финансовых транзакций"""

    def execute_transaction(self, transaction:Transaction) -> int:
        """Проводит транзакцию и изменяет баланс счёта"""

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is not None:
            raise ValueError("Транзакция уже имеет идентификатор")

        if transaction.account.object_number is None:
            raise ValueError("Счёт должен быть сохранен в базе")

        if not transaction.is_active:
            raise ValueError("Нельзя провести неактивную транзакцию")

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
                (
                    transaction.action_date.isoformat(),
                    amount_minor,
                    transaction.operation.value,
                    transaction.category,
                    transaction.account.object_number,
                    transaction.comment,
                    int(transaction.is_active),
                )
            )

            if transaction.operation == OperationType.INCOME:

                amount_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor + ?
                    WHERE id = ?
                    """,
                    (
                        amount_minor,
                        transaction.account.object_number,
                    )
                )

            elif transaction.operation == OperationType.EXPENSE:
    
                amount_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    """,
                    (
                        amount_minor,
                        transaction.account.object_number,
                    )
                )

            if amount_cursor.rowcount == 0:
                raise ValueError("Счёт данной транзакции не найден")

            transaction_id = cursor.lastrowid

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        transaction.transaction_id = transaction_id

        if transaction.operation == OperationType.INCOME:
            transaction.account.balance += transaction.amount
            
        elif transaction.operation == OperationType.EXPENSE:
            transaction.account.balance -= transaction.amount
            
        return transaction.transaction_id