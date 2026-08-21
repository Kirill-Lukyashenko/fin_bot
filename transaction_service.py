from transaction import Transaction, OperationType
from database import get_connection
from money import to_minor_units
from transfer import Transfer

class TransactionService:
    """Логика поведения финансовых транзакций"""

    def execute_transaction(self, transaction:Transaction) -> int:
        """Проводит транзакцию и изменяет баланс счёта"""

        if not isinstance(transaction, Transaction):
            raise TypeError("Должен быть передан объект Transaction")

        if transaction.transaction_id is not None:
            raise ValueError("Транзакция уже имеет идентификатор")

        if transaction.account.object_number is None:
            raise ValueError("Счёт должен быть сохранен в базе")

        if not transaction.is_active:
            raise ValueError("Нельзя провести неактивную транзакцию")

        if transaction.operation not in (OperationType.INCOME, OperationType.EXPENSE,):
            raise ValueError("Через execute_transaction можно проводить только доход или расход")

        amount_minor = to_minor_units(transaction.amount)

        connection = get_connection()

        try:

            account_row = connection.execute(
                """
                SELECT is_active
                FROM accounts
                WHERE id = ?
                """,
                (
                    transaction.account.object_number,
                )
            ).fetchone()

            if account_row is None:
                raise ValueError("Счёт данной транзакции не найден")

            if not bool(account_row["is_active"]):
                raise ValueError("Нельзя провести транзакцию по неактивному счёту")

            cursor = connection.execute(
                """
                INSERT INTO transactions (
                    action_date,
                    amount_minor,
                    operation,
                    category,
                    account_id,
                    comment,
                    is_active
                )

                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    transaction.action_date.isoformat(),
                    amount_minor,
                    transaction.operation.value,
                    transaction.category,
                    transaction.account.object_number,
                    transaction.comment,
                    int(transaction.is_active),
                )
            )

            if transaction.operation == OperationType.INCOME:

                amount_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor + ?
                    WHERE id = ?
                    """,
                    (
                        amount_minor,
                        transaction.account.object_number,
                    )
                )

            elif transaction.operation == OperationType.EXPENSE:
    
                amount_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    """,
                    (
                        amount_minor,
                        transaction.account.object_number,
                    )
                )

            if amount_cursor.rowcount == 0:
                raise ValueError("Счёт данной транзакции не найден")

            transaction_id = cursor.lastrowid

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        transaction.transaction_id = transaction_id

        if transaction.operation == OperationType.INCOME:
            transaction.account.balance += transaction.amount
            
        elif transaction.operation == OperationType.EXPENSE:
            transaction.account.balance -= transaction.amount
            
        return transaction.transaction_id
    
    def cancel_transaction(self, transaction_id: int) -> None:
        """Функция отменяет транзакцию"""

        if type(transaction_id) is not int:
            raise TypeError("Идентификатор транзакции должен быть целочисленным")

        if transaction_id <= 0:
            raise ValueError("Идентификатор транзакции должен быть больше нуля")

        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    account_id,
                    operation,
                    amount_minor,
                    is_active,
                    transfer_id
                FROM transactions
                WHERE id = ?
                """,
                (
                    transaction_id,
                )
            ).fetchone()

            if row is None:
                raise ValueError("Транзакции с таким идентификатором не существует")

            if row["transfer_id"] is not None:
                raise ValueError("Эта транзакция является частью перевода, Необходимо отменять весь перевод")

            if not bool(row["is_active"]):
                raise ValueError("Транзакция уже отменена")

            operation = OperationType(row["operation"])

            transaction_cursor = connection.execute(
                            """
                            UPDATE transactions
                            SET is_active = 0
                            WHERE id = ?
                            AND is_active = 1
                            """,
                            (
                                transaction_id,
                            )
            )

            if transaction_cursor.rowcount == 0:
                raise ValueError("Транзакция уже отменена")

            if operation == OperationType.EXPENSE:
                account_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor + ?
                    WHERE id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["account_id"],
                    )
                )

            elif operation == OperationType.INCOME:
                account_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["account_id"],
                    )
                )

            else:
                raise ValueError("Неизвестный тип финансововой операции")

            if account_cursor.rowcount == 0:
                raise ValueError("Счёта с таким идентификатором не найдено в базе")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def restore_transaction(self, transaction_id: int) -> None:
        """Функция восстанавливает деактивированную транзакцию"""

        if type(transaction_id) is not int:
            raise TypeError("Идентификатор транзакции должен быть целочисленным")

        if transaction_id <= 0:
            raise ValueError("Идентификатор транзакции должен быть больше нуля")

        connection = get_connection()

        try:

            row = connection.execute(
                """
                SELECT
                    account_id,
                    operation,
                    amount_minor,
                    is_active,
                    transfer_id
                FROM transactions
                WHERE id = ?
                """,
                (
                    transaction_id,
                )
            ).fetchone()

            if row is None:
                raise ValueError("Транзакции с таким идентификатором не существует")

            if row["transfer_id"] is not None:
                raise ValueError("Эта транзакция является частью перевода, Необходимо восстанавливать весь перевод")
    
            if bool(row["is_active"]):
                raise ValueError("Транзакция уже восстановлена")

            operation = OperationType(row["operation"])

            transaction_cursor = connection.execute(
                """
                UPDATE transactions
                SET is_active = 1
                WHERE id = ?
                AND is_active = 0
                """,
                (
                    transaction_id,
                )
            )

            if transaction_cursor.rowcount == 0:
                raise ValueError("Транзакция уже восстановлена")

            if operation == OperationType.INCOME:
                account_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor + ?
                    WHERE id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["account_id"],
                    )
                )

            elif operation == OperationType.EXPENSE:
                account_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["account_id"],
                    )
                )

            else:
                raise ValueError("Неизвестный тип финансовой операции")

            if account_cursor.rowcount == 0:
                raise ValueError("Счёта с таким идентификатором не найдено в базе")
            
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def execute_transfer(self, transfer : Transfer) -> int:
        """Функция выполняет перевод средств с одного счёта на другой"""

        if not isinstance(transfer, Transfer):
            raise TypeError("Должен быть передан объект трансфер")

        if transfer.transfer_id is not None:
            raise ValueError("Перевод уже имеет идентификатор")

        if not transfer.is_active:
            raise ValueError("Нельзя провести неактивный перевод")

        amount_minor = to_minor_units(transfer.amount)

        connection = get_connection()

        try:
            source_account= connection.execute(
                """
                SELECT
                    currency,
                    is_active
                FROM accounts
                WHERE
                    id = ?
                """,
                (
                    transfer.source_account_id,
                )
            ).fetchone()

            dest_account = connection.execute(
                """
                SELECT
                    currency,
                    is_active
                FROM accounts
                WHERE
                    id = ?
                """,
                (
                    transfer.dest_account_id,
                )
            ).fetchone()

            if source_account is None:
                raise ValueError("Счёт отправителя не найден")

            if dest_account is None:
                raise ValueError("Счёт получателя не найден")

            if not bool(source_account["is_active"]):
                raise ValueError("Счёт отправителя не активен")

            if not bool(dest_account["is_active"]):
                raise ValueError("Счёт получателя неактивен")

            if source_account["currency"] != dest_account["currency"]:
                raise ValueError("Валютные переводы пока недоступны!")

            transfer_cursor = connection.execute(
                """
                INSERT INTO transfers
                    (is_active)
                VALUES (?)
                """,
                (
                    int(transfer.is_active),
                )
            )

            transfer_id = transfer_cursor.lastrowid

            connection.execute(
                """
                INSERT INTO transactions (
                    action_date,
                    amount_minor,
                    operation,
                    category,
                    account_id,
                    comment,
                    is_active,
                    transfer_id
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    transfer.action_date.isoformat(),
                    amount_minor,
                    OperationType.TRANSFER_OUT.value,
                    transfer.CATEGORY,
                    transfer.source_account_id,
                    transfer.comment,
                    int(transfer.is_active),
                    transfer_id,
                )
            )

            connection.execute(
                """
                INSERT INTO transactions (
                    action_date,
                    amount_minor,
                    operation,
                    category,
                    account_id,
                    comment,
                    is_active,
                    transfer_id
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    transfer.action_date.isoformat(),
                    amount_minor,
                    OperationType.TRANSFER_IN.value,
                    transfer.CATEGORY,
                    transfer.dest_account_id,
                    transfer.comment,
                    int(transfer.is_active),
                    transfer_id,
                )
            )

            source_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor - ?
                WHERE id = ?
                """,
                (
                    amount_minor,
                    transfer.source_account_id
                )
            )

            if source_cursor.rowcount == 0:
                raise ValueError("Не удалось изменить баланс счёта отправителя")

            dest_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor + ?
                WHERE id = ?
                """,
                (
                    amount_minor,
                    transfer.dest_account_id
                )
            )

            if dest_cursor.rowcount == 0:
                raise ValueError("Не удалось изменить баланс счёта получателя")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        transfer.transfer_id = transfer_id
        
        return transfer.transfer_id

    def cancel_transfer(self, transfer_id: int) -> None:
        """Функция выполняет деактивацию перевода между счетами"""

        if type(transfer_id) is not int:
            raise TypeError("Идентификатор перевода должен быть целочисленным")

        if transfer_id <= 0:
            raise ValueError("Идентификатор перевода должен быть больше нуля")

        connection = get_connection()

        try:
            transfer_row = connection.execute(
                """
                SELECT
                    is_active
                FROM transfers
                WHERE id = ?
                """,
                (
                    transfer_id,
                )
            ).fetchone()

            if transfer_row is None:
                raise ValueError("Перевод не найден")

            if not bool(transfer_row["is_active"]):
                raise ValueError("Перевод уже деактивирован")

            transaction_in_transfer_row = connection.execute(
                """
                SELECT
                    amount_minor,
                    is_active,
                    account_id
                FROM transactions
                WHERE transfer_id = ?
                AND operation = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                )
            ).fetchone()

            if transaction_in_transfer_row is None:
                raise ValueError("Транзакции с таким идентификатором не существует")

            if not bool(transaction_in_transfer_row["is_active"]):
                raise ValueError("Транзакция уже деактивирована")

            dest_acc = int(transaction_in_transfer_row["account_id"])

            transaction_out_transfer_row = connection.execute(
                """
                SELECT
                    amount_minor,
                    is_active,
                    account_id
                FROM transactions
                WHERE transfer_id = ?
                AND operation = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_OUT.value,
                )
            ).fetchone()

            if transaction_out_transfer_row is None:
                raise ValueError("Транзакции с таким идентификатором не существует")

            if not bool(transaction_out_transfer_row["is_active"]):
                raise ValueError("Транзакция уже деактивирована")

            source_acc = int(transaction_out_transfer_row["account_id"])

            transfer_cursor = connection.execute(
                """
                UPDATE transfers
                SET is_active = 0
                WHERE id = ?
                AND is_active = 1
                """,
                (
                    transfer_id,
                )
            )

            if transfer_cursor.rowcount == 0:
                raise ValueError("Перевод не найден")

            transaction_cursor = connection.execute(
                """
                UPDATE transactions
                SET is_active = 0
                WHERE transfer_id = ?
                AND is_active = 1
                """,
                (
                    transfer_id,
                )
            )

            if transaction_cursor.rowcount != 2:
                raise ValueError("Не удалось деактивировать обе транзакции перевода")

            source_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor + ?
                WHERE id = ?
                """,
                (
                    transaction_out_transfer_row["amount_minor"],
                    source_acc,
                )
            )

            if source_acc_cursor.rowcount == 0:
                raise ValueError("Аккаунт не найден в базе")

            dest_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor - ?
                WHERE id = ?
                """,
                (
                    transaction_in_transfer_row["amount_minor"],
                    dest_acc,
                )
            )

            if dest_acc_cursor.rowcount == 0:
                raise ValueError("Аккаунт не найден в базе")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def restore_transfer(self, transfer_id : int) -> None:
        """Функция активирует перевод"""

        if type(transfer_id) is not int:
            raise TypeError("Идентификатор должен быть целочисленным")

        if transfer_id <= 0 :
            raise ValueError("Идентификатор должен быть больше нуля")

        connection = get_connection()

        try:

            transfer_row = connection.execute(
                """
                SELECT
                    is_active
                FROM transfers
                WHERE id = ?
                """,
                (
                    transfer_id,
                )
            ).fetchone()

            if transfer_row is None:
                raise ValueError("Перевод с таким идентификатором не найден")

            if bool(transfer_row["is_active"]):
                raise ValueError("Перевод уже активен")

            transaction_out_transfer_row = connection.execute(
                """
                SELECT
                    amount_minor,
                    is_active,
                    account_id
                FROM transactions
                WHERE transfer_id =?
                AND operation = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_OUT.value,
                )
            ).fetchone()

            if transaction_out_transfer_row is None:
                raise ValueError("Транзакции с таким идентификатором перевода не существует")

            if bool(transaction_out_transfer_row["is_active"]):
                raise ValueError("Транзакция уже активна")

            source_acc = int(transaction_out_transfer_row["account_id"])

            transaction_in_transfer_row = connection.execute(
                """
                SELECT
                    amount_minor,
                    is_active,
                    account_id
                FROM transactions
                WHERE transfer_id = ?
                AND operation = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                )
            ).fetchone()

            if transaction_in_transfer_row is None:
                raise ValueError("Транзакции с таким идентификатором перевода не существует")

            if bool(transaction_in_transfer_row["is_active"]):
                raise ValueError("Транзакция уже активна")

            dest_acc = int(transaction_in_transfer_row["account_id"])

            transfer_cursor = connection.execute(
                """
                UPDATE transfers
                SET is_active = 1
                WHERE id = ?
                AND is_active = 0
                """,
                (
                    transfer_id,
                )
            )

            if transfer_cursor.rowcount == 0:
                raise ValueError("Перевод с таким идентификатором не найден")

            transaction_cursor = connection.execute(
                """
                UPDATE transactions
                SET is_active = 1
                WHERE transfer_id = ?
                AND is_active = 0
                """,
                (
                    transfer_id,
                )
            )

            if transaction_cursor.rowcount != 2:
                raise ValueError("Не удалось активировать обе транзакции перевода")

            source_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor - ?
                WHERE id = ?
                """,
                (
                    transaction_out_transfer_row["amount_minor"],
                    source_acc,
                )
            )

            if source_acc_cursor.rowcount == 0:
                raise ValueError("Аккаунт не найден в базе")

            dest_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor + ?
                WHERE id = ?
                """,
                (
                    transaction_in_transfer_row["amount_minor"],
                    dest_acc,
                )
            )

            if dest_acc_cursor.rowcount == 0:
                raise ValueError("Аккаунт не найден в базе")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()