from decimal import Decimal, InvalidOperation
from account import Account
from datetime import date
from enum import Enum

class OperationType(str, Enum):
    """Перечисление типов доступных операций"""
    INCOME = "Доход"
    EXPENSE = "Расход"

class Transaction:

    def __init__(self,
                 action_date : date,                                            # Дата соверщения транзакции
                 amount : str | Decimal,                                        # Сумма транзакции
                 operation : OperationType,                                     # Операция
                 category : str,                                                # Категория
                 account : Account,                                             # Счёт списания/пополнения
                 comment : str,                                                 # Комментарий
                 transaction_id : int | None = None,                            # Уникальный номер транзакции
                 is_active : bool = True                                        # Состояние транзакции
                 ):                                                                                                                                                                                                                       

        # Проверка правильности переданной даты
        if not isinstance(action_date, date):
            raise TypeError("Дата транзакции должна быть объектом date")

        self.action_date = action_date 

        # Проверка счёта
        if not isinstance(account, Account):
            raise TypeError("Счёт должен быть объектом класса Account")

        self.account = account 

        # Проверка категории
        if not isinstance(category, str):
            raise TypeError("Категория должна быть строкой")

        self.category = category.strip()                                        

        if not self.category:
            raise ValueError("Категория не может быть пустой")
        
        # Проверка правильности переданной суммы
        try:
            normalized_amount = str(amount).replace(" ", "").replace(",", ".")
            self.amount = Decimal(normalized_amount)

        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Передано некорректное значение суммы")

        if self.amount <=0:
            raise ValueError("Сумма не может быть меньше или равна нулю")

        # Проверка правильности введеного коментария
        if not isinstance(comment, str):
            raise TypeError("Комментарий должен быть строкой")

        self.comment = comment.strip()                                          

        if not self.comment:
            raise ValueError("Комментарий не может быть пустым")

        # Проверка правильности операции
        if not isinstance(operation, OperationType):
            raise TypeError("Неверная операция")

        self.operation = operation  

        # Проверка правильности транзакции
        if transaction_id is not None:
            if not isinstance(transaction_id, int):
                raise TypeError("Идентификатор транзакции должен быть int или None")

            if transaction_id <= 0:
                raise ValueError("Идентификатор транзакции должен быть больше нуля")

        self.transaction_id = transaction_id

        # Проверка правильности активного состояния
        if not isinstance(is_active, bool):
            raise TypeError("Состояние транзакции должно иметь тип bool")

        self.is_active = is_active   

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