from decimal import Decimal, ROUND_HALF_UP


MINOR_UNIT = Decimal("0.01")
MINOR_FACTOR = Decimal("100")

def to_minor_units(amount: Decimal) -> int:
    """
    Преобразует денежную сумму Decimal 
    в целое количество минимальных единиц.
    """

    if not isinstance(amount, Decimal):
        raise TypeError("Сумма должна быть объектом Decimal")

    if not amount.is_finite():
        raise ValueError("Сумма должна быть конечным числом")

    normalized_amount = amount.quantize(MINOR_UNIT, rounding=ROUND_HALF_UP)

    return int(normalized_amount * MINOR_FACTOR)

def from_minor_units(amount_minor :int) -> Decimal:
    """
        Преобразует целое количество минимальных единиц
        обратно в Decimal
    """

    if type(amount_minor) is not int:
        raise TypeError("Количество минимальных единиц должно иметь тип int")

    return (Decimal(amount_minor) / MINOR_FACTOR).quantize(MINOR_UNIT)
