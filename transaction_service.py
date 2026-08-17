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

        
