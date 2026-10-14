
from decimal import Decimal, InvalidOperation
from money import to_minor_units, from_minor_units

def validate_id(
        account_id : int | None = None,
        user_id : int | None = None,
        transaction_id : int | None = None,
        transfer_id : int | None = None,
        obligation_id : int | None = None
        ):
    """Функция валидирует все переданные идентификаторы"""

    identifiers = {
        "Идентификатор счёта": account_id,
        "Идентификатор пользователя": user_id,
        "Идентификатор транзакции": transaction_id,
        "Идентификатор перевода": transfer_id,
        "Идентификатор обязательства": obligation_id
    }

    for name, value in identifiers.items():

        if value is None:
            continue

        if type(value) is not int:
            raise TypeError(f"{name} должен быть целочисленным")

        if value <= 0 :
            raise ValueError(f"{name} должен быть больше нуля")


def validate_amount(amount : Decimal | str) -> Decimal:
    """Функция возвращает подготовленное число формата Decimal"""

    if not isinstance(amount, (Decimal, str)):
        raise TypeError("Некорректный тип суммы")

    try:

        normalized_amount = str(amount).replace(" ", "").replace(",", ".")
        decimal_amount = Decimal(normalized_amount)

    except InvalidOperation:

        raise ValueError("Неккоректная сумма")

    if not decimal_amount.is_finite():
        raise ValueError("Сумма должна быть конечным числом")

    amount_minor = to_minor_units(decimal_amount)

    if amount_minor <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    pure_amount = from_minor_units(amount_minor)

    return pure_amount