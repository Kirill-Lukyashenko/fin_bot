from decimal import Decimal

class Account:

    def __init__(self,
                 object_number : int,
                 source : str,
                 acc_type : str,
                 product_name : str | None,
                 requisites : str | None,
                 balance : str | Decimal,
                 currency : str,
                 limit : str | Decimal | None = None,
                 is_active : bool = True
                 ):
        self.object_number = object_number                                          # Порядковый номер места хранения денег
        self.source = source                                                        # Место хранения денег
        self.acc_type = acc_type                                                    # Тип места хранения
        self.product_name = product_name                                            # Название продукта где хранятся деньги
        self.requisites = requisites                                                # Реквизиты карты/счёта
        self.balance = Decimal(balance)                                             # Актуальный баланс
        self.currency = currency                                                    # Валюта хранения
        self.limit = Decimal(limit) if limit is not None else None                  # Лимит (используется только для кредиток)
        self.is_active = is_active                                                  # Активен ли счёт в данный момент

    def acc_activate(self):
        self.is_active = True

    def acc_deactivate(self):
        self.is_active = False

    def check_state(self):
        if self.is_active:
            return "Запрашиваемый счёт активен"
        else:
            return "Запрашиваемый счёт деактивирован"

