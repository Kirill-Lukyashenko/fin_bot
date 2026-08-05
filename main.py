from account import Account
from account_repository import AccountRepository
from database import create_tables


def main() -> None:
    create_tables()

    kaspi_gold = Account(
        object_number=None,
        source="Kaspi",
        acc_type="Карта",
        product_name="Gold",
        requisites="4084",
        balance="1000.00",
        currency="KZT",
        limit=None,
        is_active=True,
    )

    repository = AccountRepository()

    account_id = repository.add_account(kaspi_gold)

    print(f"Счёт сохранён с идентификатором: {account_id}")
    print(f"Идентификатор внутри объекта: {kaspi_gold.object_number}")


if __name__ == "__main__":
    main()