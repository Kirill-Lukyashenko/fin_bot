from account import Account
from transaction import Transaction
from transaction_repository import TransactionRepository
from account_repository import AccountRepository
from database import create_tables
from decimal import Decimal
from datetime import date
from transaction import OperationType


def main() -> None:
    create_tables()

    repository = AccountRepository()
    tr_rep = TransactionRepository()

    kaspi_acc = repository.get_account_by_id(1)
    BCC_acc = repository.get_account_by_id(2)

    transaction = Transaction(
        action_date= date(2026,8,17),
        amount= "20000.00",
        operation= OperationType.INCOME,
        category= "Перевод",
        account= kaspi_acc,
        comment= "Перевел с БЦК"
        )

    tr_rep.add_transaction(transaction)
    
    
if __name__ == "__main__":
    main()