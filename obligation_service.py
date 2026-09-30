from obligation_repository import ObligationRepository
from obligation import Obligation

class ObligationService:

    def __init__(self, obligation_repository : ObligationRepository):

        self.obligation_repository = obligation_repository

    def register_existing_obligation(self, obligation : Obligation, user_id : int) -> int:

        if not isinstance(obligation, Obligation):
            raise TypeError("Обязательство должно быть объектом Obligation")

        if obligation.obligation_id is not None:
            raise ValueError("Обязательство уже имеет идентификатор")

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if obligation.user_id != user_id:
            raise ValueError("Обязательство не принадлежит указанному пользователю")

        return self.obligation_repository.add_obligation(obligation)
