

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

        