from decimal import Decimal
from account import Account
from datetime import date
from enum import Enum

class OperationType(Enum):
    """Перечисление типов доступных операций"""
    INCOME = "Доход"
    EXPENSE = "Расход"

class Transaction:

    def __init__(self,
                 action_date : date,
                 amount : str | Decimal,
                 operation : OperationType,
                 category : str,
                 account : Account,
                 comment : str,
                 transaction_id : int | None = None,
                 is_active : bool = True
                 ):
        self.action_date = action_date                                  # Дата соверщения транзакции
        self.amount = Decimal(amount)                                   # Сумма транзакции
        self.operation = operation                                      # Тип операции
        self.category = category                                        # Категория
        self.account = account                                          # Счёт списания/пополнения
        self.comment = comment.strip()                                  # Комментарий
        self.transaction_id = transaction_id                            # Уникальный номер транзакции
        self.is_active = is_active                                      # Состояние транзакции

        # Проверка правильности переданной суммы
        if self.amount <=0:
            raise ValueError("Сумма не может быть меньше или равна нулю")

        # Проверка правильности введеного коментария
        if not self.comment:
            raise ValueError("Комментарий не может быть пустым")

        # Проверка правильности операции
        if not isinstance(self.operation, OperationType):
            raise TypeError("Неверная операция")

    def check_state(self) -> str:
        """Проверка состояния транзакции"""
        if self.is_active :
            return "Транзакция активна"
        
        return "Транзакция отменена"

    def restore(self) -> None:
        """Восстановление транзакции"""
        self.is_active = True

    def cancel(self) -> None:
        """Отмена транзакции"""
        self.is_active = False