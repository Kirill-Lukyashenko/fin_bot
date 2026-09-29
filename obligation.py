from decimal import Decimal, InvalidOperation
from datetime import date
from enum import Enum

class ObligationType(str, Enum):
    """Перечисление типов доступных обязательств"""
    DEBT = "Долг"
    LOAN = "Займ"

class CurrencyType(str, Enum):
    """Перечисление доступных валют"""
    KZT = "KZT"                                                                                     # Тенге
    RUB = "RUB"                                                                                     # Рубли
    USD = "USD"                                                                                     # Доллары
    EUR = "EUR"                                                                                     # Евро
    CNY = "CNY"                                                                                     # Юань
    TRY = "TRY"                                                                                     # Лира
    AED = "AED"                                                                                     # Дирхам
    KGS = "KGS"                                                                                     # Сом
    UZS = "UZS"                                                                                     # Сум

class Obligation:
    """Класс с описанием таблицы обязательств"""
    def __init__(self,
                 obligation_id : int | None,                                                        # Идентификатор обязательства
                 user_id : int,                                                                     # Идентификатор пользователя
                 counterparty : str,                                                                # Контрагент
                 obligation_type : ObligationType,                                                  # Тип обязательства
                 amount : str| Decimal,                                                             # Первоначальная сумма обязательства
                 remaining_amount : str | Decimal,                                                  # Оставшаяся часть обязательства
                 currency : CurrencyType,                                                           # Валюта
                 start_date : date,                                                                 # Дата выдачи обязательства
                 end_date : date | None,                                                            # Дата возврата обязательства
                 comment : str,                                                                     # Комментарий
                 is_active : bool = True                                                            # Состояние обязательства
                 ):

        # Валидация идентификатора обязательства
        if obligation_id is not None:

            if type(obligation_id) is not int:
                raise TypeError("Идентификатор обязательства должен быть целочисленным")

            if obligation_id <= 0:
                raise ValueError("Идентификатор обязательства должен быть больше нуля")

        # Валидация идентификатора пользователя
        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        # Валидация контрагента
        if not isinstance(counterparty, str):
            raise TypeError("Контрагент должен быть строкой")

        counterparty = counterparty.strip()

        if not counterparty:
            raise ValueError("Контрагент не может быть пустым")

        # Валидация типа обязательства
        if not isinstance(obligation_type, ObligationType):
            raise TypeError("Неверный тип обязательства")

        # Валидация начальной суммы обязательства
        try:
            normalized_amount = str(amount).replace(" ", "").replace(",", ".")
            pure_amount = Decimal(normalized_amount)

        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Неверно указана начальная сумма")

        if not pure_amount.is_finite():
            raise ValueError("Начальная сумма должна быть конечным числом")

        if pure_amount <= 0:
            raise ValueError("Начальная сумма должна быть больше нуля")

        # Валидация оставшейся суммы обязательства
        try:
            normalized_remaining_amount = str(remaining_amount).replace(" ", "").replace(",",".")
            pure_remaining_amount = Decimal(normalized_remaining_amount)

        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Неверно указана оставшаяся сумма")

        if not pure_remaining_amount.is_finite():
            raise ValueError("Оставшаяся сумма должна быть конечным числом")

        if pure_remaining_amount < 0:
            raise ValueError("Оставшаяся сумма не может быть меньше нуля")

        if pure_remaining_amount > pure_amount:
            raise ValueError("Оставшаяся сумма не может превышать первоначальную сумму")

        # Валидация валюты
        if not isinstance(currency, CurrencyType):
            raise TypeError("Неверная валюта")

        # Валидация даты начала
        if not isinstance(start_date, date):
            raise TypeError("Дата должна быть объектом date")

        # Валидация даты окончания
        if end_date is not None:

            if not isinstance(end_date, date):
                raise TypeError("Дата должна быть объектом date")

            if end_date < start_date:
                raise ValueError("Дата окончания не может быть меньше даты начала")

        # Валидация комментария
        if not isinstance(comment, str):
            raise TypeError("Комментарий должен быть строкой")

        comment = comment.strip()

        if not comment:
            raise ValueError("Комментарий не может быть пустым")

        # Валидация статуса обязательства
        if not isinstance(is_active, bool):
            raise TypeError("Состояние обязательства должно иметь тип bool")
        
        # Построение объекта
        self.obligation_id = obligation_id
        self.user_id = user_id
        self.counterparty = counterparty
        self.obligation_type = obligation_type
        self.amount = pure_amount
        self.remaining_amount = pure_remaining_amount
        self.currency = currency
        self.start_date = start_date
        self.end_date = end_date
        self.comment = comment
        self.is_active = is_active