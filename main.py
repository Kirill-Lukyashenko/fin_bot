from account import Account
from transaction import Transaction
from transaction_repository import TransactionRepository
from account_repository import AccountRepository
from database import create_tables
from decimal import Decimal
from datetime import date
from transaction import OperationType
from transaction_service import TransactionService
from transfer import Transfer


def main() -> None:
    """
    create_tables()

    check_work = "yes"

    while check_work == "yes":

        print("Работаем дальше?:")

        check_work = str(input())

        if check_work != "yes":
            break

        print("Источник: ", end = " ")
        a_source = str(input())
        print("Тип счёта: ", end = " ")
        a_acc_type = str(input())
        print("Имя продукта: ", end = " ")
        a_product_name = str(input())
        print("Реквизиты: ", end = " ")
        a_requisites = str(input())
        print("Баланс: ", end = " ")
        a_balance = str(input())
        print("Валюта: ", end = " ")
        a_currency = str(input())

        account = Account(
            object_number= None,
            source= a_source,
            acc_type= a_acc_type,
            product_name= a_product_name,
            requisites= a_requisites,
            balance = a_balance,
            currency= a_currency
        )

        acc = AccountRepository()

        acc.add_account(account)
        """

    acc_rep = AccountRepository()
    tr_service = TransactionService()

    account = acc_rep.get_account_by_id(3)

    """
    transaction = Transaction(
        action_date=date(2026, 8, 20),
        amount=Decimal("405000.00"),
        operation=OperationType.EXPENSE,
        category="ЗАРПЛАТА",
        account=account,
        comment="Получил зарплату"
    )

    tr_service.execute_transaction(transaction)
    """
    #tr_service.cancel_transaction(7)
    

    """
    transfer = Transfer(
        action_date=date(2026, 8, 21),
        source_account_id=2,
        dest_account_id=3,
        amount=Decimal("10000.00"),
        comment="Тестовый перевод с BCC на Фридом"
    )

    tr_service.execute_transfer(transfer)
    """
    #tr_service.cancel_transfer(3)

    """
    account = acc_rep.get_account_by_id(3)
    account.balance = Decimal("0.00")
    acc_rep.update_account(account)
    """

if __name__ == "__main__":
    main()