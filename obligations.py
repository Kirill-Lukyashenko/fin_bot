from decimal import Decimal, InvalidOperation
from datetime import date
from enum import Enum

class ObligationType(str, Enum):
    """Перечисление типов доступных обязательств"""
    DEBT = "Долг"
    LOAN = "Займ"

class Obligation:
    """Класс с описанием таблицы обязательств"""
    def __init__(self,
                 obligation_id : int | None,
                 user_id : int,
                 obligation_type : ObligationType,
                 amount : str| Decimal,
                 currency : str,
                 start_date : date,
                 end_date : date | None,
                 comment : str,
                 is_active : bool = True
                 ):
        pass