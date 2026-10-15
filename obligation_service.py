from obligation_repository import ObligationRepository
from transaction_repository import TransactionRepository
from account_repository import AccountRepository

from obligation import Obligation, ObligationType
from transaction import Transaction, OperationType
from account import Account

from database import get_connection

from decimal import Decimal
from datetime import date

from money import to_minor_units, from_minor_units

from utils.validation import validate_id, validate_amount

class ObligationService:

    def __init__(self, obligation_repository : ObligationRepository, transaction_repository : TransactionRepository, account_repository : AccountRepository):

        self.obligation_repository = obligation_repository
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository

    def register_existing_obligation(self, obligation : Obligation, user_id : int) -> int:

        if not isinstance(obligation, Obligation):
            raise TypeError("Обязательство должно быть объектом Obligation")

        if obligation.obligation_id is not None:
            raise ValueError("Обязательство уже имеет идентификатор")

        validate_id(user_id= user_id)

        if obligation.user_id != user_id:
            raise ValueError("Обязательство не принадлежит указанному пользователю")

        return self.obligation_repository.add_obligation(obligation, user_id)

    def create_obligation(self, obligation : Obligation, account : Account, user_id : int) -> int:
        """Функция создает новое обязательство"""

        if not isinstance(obligation, Obligation):
            raise TypeError("Обязательство должно быть объектом Obligation")

        if obligation.obligation_id is not None:
            raise ValueError("Обязательство уже имеет идентификатор")

        if not isinstance(account, Account):
            raise TypeError("Счёт должен быть объектом Account")

        if account.object_number is None:
            raise ValueError("Счёт сначала должен быть сохранён в базе")

        validate_id(user_id= user_id)

        if obligation.user_id != user_id:
            raise ValueError("Обязательство не принадлежит указанному пользователю")

        if account.user_id != user_id:
            raise ValueError("Счёт не принадлежит указанному пользователю")

        if not account.is_active:
            raise ValueError("Нельзя использовать неактивный счёт")

        if account.currency != obligation.currency.value:
            raise ValueError("Валюта счёта не совпадает с валютой обязательства")

        if obligation.obligation_type == ObligationType.DEBT:

            transaction = Transaction(
                action_date= obligation.start_date,
                amount= obligation.amount,
                operation= OperationType.INCOME,
                category= ObligationType.DEBT.value,
                account= account,
                comment= f"Получил деньги в долг: {obligation.counterparty}",
                transaction_id= None,
                transfer_id= None,
                is_active= True
            )

        elif obligation.obligation_type == ObligationType.LOAN:

            transaction = Transaction(
                action_date= obligation.start_date,
                amount= obligation.amount,
                operation= OperationType.EXPENSE,
                category= ObligationType.LOAN.value,
                account= account,
                comment= f"Выдача займа: {obligation.counterparty}",
                transaction_id= None,
                transfer_id= None,
                is_active= True
            )

        else:

            raise ValueError("Неизвестный тип обязательства")

        connection = get_connection()

        try:

            self.obligation_repository.add_obligation_in_transaction(obligation, connection, user_id)
            

            if obligation.obligation_type == ObligationType.DEBT:

                self.account_repository.increase_balance_in_transaction(account.object_number, obligation.amount, user_id, connection)

            elif obligation.obligation_type == ObligationType.LOAN:

                self.account_repository.decrease_balance_in_transaction(account.object_number, obligation.amount, user_id, connection)

            self.transaction_repository.add_transaction_in_transaction(transaction, user_id, connection)

            connection.commit()

            return obligation.obligation_id

        except Exception:
            connection.rollback()

            obligation.obligation_id = None
            transaction.transaction_id = None

            raise

        finally:
            connection.close()
        
    def repay_obligation(self, obligation_id : int, account : Account, repayment_amount : Decimal | str, repayment_date : date, user_id : int) -> None:
        """Функция выполняет частичное или полное погашение обязательства"""

        if obligation_id is None or user_id is None:
            raise ValueError("Идентификаторы обязательства и пользователя обязательны")

        validate_id(obligation_id= obligation_id, user_id= user_id)

        if not isinstance(account, Account):
            raise TypeError("Счёт должен быть объектом Account")

        if account.object_number is None:
            raise ValueError("Счёт должен быть сохранен в базе")

        validate_id(account_id=account.object_number)

        pure_amount = validate_amount(repayment_amount)

        if not isinstance(repayment_date, date):
            raise TypeError("Дата погашения должна быть объектом date")

        if account.user_id != user_id:
            raise ValueError("Счёт не принадлежит указанному пользователю")

        if not account.is_active:
            raise ValueError("Счёт не может быть деактивированным")

        connection = get_connection()

        try:

            connection.execute(
                """
                BEGIN IMMEDIATE
                """
            )

            obligation = self.obligation_repository.get_obligation_by_id_in_transaction(obligation_id= obligation_id, user_id= user_id, connection= connection)

            if obligation is None:
                raise ValueError("Обязательство не найдено")

            if not obligation.is_active:
                raise ValueError("Обязательство уже закрыто")

            if obligation.currency.value != account.currency:
                raise ValueError("Валюта счёта должна совпадать с валютой обязательства")

            if pure_amount > obligation.remaining_amount:
                raise ValueError("Сумма погашения превышает остаток обязательства")

            if repayment_date < obligation.start_date:
                raise ValueError("Дата погашения не может быть раньше даты возникновения обязательства")

            connection.commit()

        except Exception:

            connection.rollback()
            raise

        finally:

            connection.close()
        