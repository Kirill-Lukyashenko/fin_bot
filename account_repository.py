from account import Account
from database import get_connection
from money import to_minor_units

class AccountRepository:
    """Описание работы с таблицей accounts"""

    def add_account(self, account : Account) -> int:
        """Функция добавляет новый счёт в базу"""

        if not isinstance(account, Account):
            raise TypeError("Должен быть передан объект Account")

        if account.object_number is not None:
            raise ValueError("Этот счёт уже имеет идентификатор")

        balance_minor = to_minor_units(account.balance)

        limit_minor = (
            to_minor_units(account.limit)
            if account.limit is not None
            else None
            )

        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO accounts (
                    source,
                    acc_type,
                    product_name,
                    requisites,
                    currency,
                    balance_minor,
                    limit_minor,
                    is_active
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    account.source,
                    account.acc_type,
                    account.product_name,
                    account.requisites,
                    account.currency,
                    balance_minor,
                    limit_minor,
                    int(account.is_active),
                )
            )

            connection.commit()

            account.object_number = cursor.lastrowid

            return account.object_number


        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def gt_account_by_id(self):
        """Восстанавливает объект Account по прочитаной строке SQL"""

        
        pass