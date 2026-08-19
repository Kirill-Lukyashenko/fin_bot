from decimal import Decimal
from datetime import date

class Transfer:

    CATEGORY = "ПЕРЕВОД"

    def __init__(
            self, 
            action_date : date,
            source_account_id : int,
            dest_account_id : int,
            amount : Decimal,
            comment : str,
            transfer_id : int | None = None,
            is_active : bool = True
            ):

        if not isinstance(action_date, date):
            raise TypeError("Дата перевода должна быть объектом date")

        self.action_date = action_date

        if type(source_account_id) is not int:
            raise TypeError("Идентификатор счёта отправителя должен быть целочисленным значением")

        if source_account_id <= 0:
            raise ValueError("Идентификатор счёта отправителя должен быть больше нуля")

        if type(dest_account_id) is not int:
            raise TypeError("Идентификатор счёта отправителя должен быть целочисленным значением")
        
        if dest_account_id <= 0:
            raise ValueError("Идентификатор счёта отправителя должен быть больше нуля")

        if source_account_id == dest_account_id:
            raise ValueError("Идентфикаторы счетов отправителя и получателя не должны быть равны")

        self.source_account_id = source_account_id
        self.dest_account_id = dest_account_id

        if not isinstance(amount,Decimal):
            raise TypeError("Значение суммы перевода долнжо быть объктом Decimal")

        if amount <= 0:
            raise ValueError("Значение суммы перевода должно быть больше нуля")

        self.amount = amount

        if not isinstance(comment, str):
            raise TypeError("Комментарий должен быть объектом str")

        self.comment = comment.strip()

        if not self.comment:
            raise ValueError("Комментарий не может быть пустым")

        if transfer_id is not None:
            if not isinstance(transfer_id, int):
                raise TypeError("Идентификатор перевода должен быть int или None")

            if transfer_id <= 0:
                raise ValueError("Идентификатор перевода должен быть больше нуля")

        self.transfer_id = transfer_id

        if not isinstance(is_active, bool):
            raise TypeError("Состояние перевода должно иметь тип bool")
        
        self.is_active = is_active