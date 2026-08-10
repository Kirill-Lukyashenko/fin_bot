from transaction import Transaction
from database import get_connection
from money import to_minor_units

class TransactionRepository:
    """Описание работы с таблицей transactions"""

    def add_transactions(self, transaction : Transaction) -> int:
        pass