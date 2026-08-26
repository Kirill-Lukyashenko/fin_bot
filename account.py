from decimal import Decimal

class Account:

    def __init__(self,
                 object_number : int | None,                                        # Идентификатор счёта
                 user_id : int,                                                     # Идентификатор пользователя                                      
                 source : str,                                                      # Место хранения денег
                 acc_type : str,                                                    # Тип места хранения
                 product_name : str | None,                                         # Название продукта где хранятся деньги
                 requisites : str | None,                                           # Реквизиты карты/счёта
                 balance : str | Decimal,                                           # Актуальный баланс
                 currency : str,                                                    # Валюта хранения
                 limit : str | Decimal | None = None,                               # Лимит (используется только для кредиток)
                 is_active : bool = True                                            # Активен ли счёт в данный момент
                 ):

        # Проверка корректности переданного идентификатора счёта

        if object_number is not None:

            if type(object_number) is not int:
                raise TypeError("Идентификатор счёта должен быть целочисленным")

            if object_number <= 0:
                raise ValueError("Идентификатор счёта должен быть больше нуля")
            
        self.object_number = object_number

        # Проверка корректности переданного идентификатора пользователя

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        self.user_id = user_id

        self.source = source                                                        
        self.acc_type = acc_type                                                    
        self.product_name = product_name                                            
        self.requisites = requisites

        # Проверка корректности переданного баланса

        self.balance = Decimal(balance)

        if not self.balance.is_finite():
            raise ValueError("Баланс должен быть конечным числом")

        if self.balance < 0:
            raise ValueError("Баланс не может быть отрицательным")

                                                     
        self.currency = currency                                                    
        self.limit = Decimal(limit) if limit is not None else None

        # Проверка корректности переданного состояния счёта

        if type(is_active) is not bool:
            raise TypeError("Состояние счёта должно иметь тип bool")                  
        self.is_active = is_active                                                  

    def acc_activate(self):
        self.is_active = True

    def acc_deactivate(self):
        self.is_active = False

    def check_state(self):
        if self.is_active:
            return "Запрашиваемый счёт активен"
        else:
            return "Запрашиваемый счёт деактивирован"

