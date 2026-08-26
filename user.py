

class User:

    def __init__(self,
                 telegram_user_id : int,
                 is_active : bool = True,
                 user_id : int | None = None
                 ):


        if type(telegram_user_id) is not int:
            raise TypeError("Идентификатор пользователя Telegram должен быть целочисленым")

        if telegram_user_id <=0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        self.telegram_user_id = telegram_user_id

        if type(is_active) is not bool:
            raise TypeError("Состояние пользователя должно быть bool")

        self.is_active = is_active

        if user_id is not None:

            if type(user_id) is not int:
                raise TypeError("Идентификатор пользователя должен быть целочисленным")

            if user_id <=0 :
                raise ValueError("Идентификатор пользователя должен быть больше нуля")

        self.user_id = user_id