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

    account = repository.get_account_by_id(2)

    tr_rep.delete_transaction_by_id(1)
    
    
if __name__ == "__main__":
    main()