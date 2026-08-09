from account import Account
from account_repository import AccountRepository
from database import create_tables


def main() -> None:
    create_tables()

    repository = AccountRepository()

    accounts = repository.get_active_accounts()

    print(f"Количество счетов: {len(accounts)}")

    for account in accounts:
        print(
            account.object_number,
            account.source,
            account.product_name,
            account.balance,
            account.currency,
            account.is_active
            )

    
if __name__ == "__main__":
    main()