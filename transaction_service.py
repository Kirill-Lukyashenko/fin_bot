from transaction import Transaction, OperationType
from database import get_connection
from money import to_minor_units
from transfer import Transfer

class TransactionService:
    """Логика поведения финансовых транзакций"""

    def execute_transaction(self, transaction:Transaction, user_id : int) -> int:
        """Проводит транзакцию и изменяет баланс счёта"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0 :
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

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

        if transaction.account.user_id != user_id:
            raise ValueError("Счёт транзакции не принадлежит пользователю")

        amount_minor = to_minor_units(transaction.amount)

        connection = get_connection()

        try:

            account_row = connection.execute(
                """
                SELECT 
                    a.is_active as account_is_active,
                    u.is_active as user_is_active
                FROM accounts AS a
                JOIN users AS u
                ON
                    u.user_id = a.user_id
                WHERE a.id = ?
                AND a.user_id = ?
                """,
                (
                    transaction.account.object_number,
                    user_id,
                )
            ).fetchone()

            if account_row is None:
                raise ValueError("Счёт данной транзакции не найден")

            if not bool(account_row["account_is_active"]):
                raise ValueError("Счёт деактивирован")

            if not bool(account_row["user_is_active"]):
                raise ValueError("Пользователь деактивирован")

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
                    AND user_id = ?
                    AND is_active = 1
                    """,
                    (
                        amount_minor,
                        transaction.account.object_number,
                        user_id,
                    )
                )

            elif transaction.operation == OperationType.EXPENSE:
    
                amount_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    AND balance_minor >= ?
                    AND user_id = ?
                    AND is_active = 1
                    """,
                    (
                        amount_minor,
                        transaction.account.object_number,
                        amount_minor,
                        user_id,
                    )
                )

            if amount_cursor.rowcount == 0:
                raise ValueError("На счете недостаточно средств или счёт недоступен")

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
    
    def cancel_transaction(self, transaction_id: int, user_id : int) -> None:
        """Функция отменяет транзакцию"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")
        
        if user_id <= 0 :
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if type(transaction_id) is not int:
            raise TypeError("Идентификатор транзакции должен быть целочисленным")

        if transaction_id <= 0:
            raise ValueError("Идентификатор транзакции должен быть больше нуля")

        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    t.account_id AS transaction_account_id,
                    t.operation AS transaction_operation,
                    t.amount_minor,
                    t.is_active AS transaction_is_active,
                    t.transfer_id AS transaction_transfer
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE t.id = ?
                AND a.user_id = ?
                """,
                (
                    transaction_id,
                    user_id,
                )
            ).fetchone()

            if row is None:
                raise ValueError("Транзакция не существует")

            if row["transaction_transfer"] is not None:
                raise ValueError("Эта транзакция является частью перевода, Необходимо отменять весь перевод")

            if not bool(row["transaction_is_active"]):
                raise ValueError("Транзакция уже отменена")

            operation = OperationType(row["transaction_operation"])

            transaction_cursor = connection.execute(
                            """
                            UPDATE transactions
                            SET is_active = 0
                            WHERE id = ?
                            AND is_active = 1
                            AND transfer_id IS NULL
                            AND EXISTS (
                                SELECT 1
                                FROM accounts AS a
                                WHERE a.id = transactions.account_id
                                AND a.user_id = ?
                            )
                            """,
                            (
                                transaction_id,
                                user_id,
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
                    AND user_id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["transaction_account_id"],
                        user_id,
                    )
                )

            elif operation == OperationType.INCOME:
                account_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    AND balance_minor >= ?
                    AND user_id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["transaction_account_id"],
                        row["amount_minor"],
                        user_id,
                    )
                )

            else:
                raise ValueError("Неизвестный тип финансовой операции")

            if account_cursor.rowcount == 0:
                raise ValueError("Не удалось скорректировать баланс счёта")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def restore_transaction(self, transaction_id: int, user_id : int) -> None:
        """Функция восстанавливает деактивированную транзакцию"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0 :
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if type(transaction_id) is not int:
            raise TypeError("Идентификатор транзакции должен быть целочисленным")

        if transaction_id <= 0:
            raise ValueError("Идентификатор транзакции должен быть больше нуля")

        connection = get_connection()

        try:

            row = connection.execute(
                """
                SELECT
                    t.account_id AS transaction_account_id,
                    t.operation AS transaction_operation,
                    t.amount_minor,
                    t.is_active AS transaction_is_active,
                    t.transfer_id AS transaction_transfer_id
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE t.id = ?
                AND a.user_id = ?
                """,
                (
                    transaction_id,
                    user_id,
                )
            ).fetchone()

            if row is None:
                raise ValueError("Транзакция не существует")

            if row["transaction_transfer_id"] is not None:
                raise ValueError("Эта транзакция является частью перевода, Необходимо восстанавливать весь перевод")
    
            if bool(row["transaction_is_active"]):
                raise ValueError("Транзакция уже восстановлена")

            operation = OperationType(row["transaction_operation"])

            transaction_cursor = connection.execute(
                """
                UPDATE transactions
                SET is_active = 1
                WHERE id = ?
                AND is_active = 0
                AND transfer_id IS NULL
                AND EXISTS(
                    SELECT 1
                    FROM accounts AS a
                    WHERE a.id = transactions.account_id
                    AND a.user_id = ?
                )
                """,
                (
                    transaction_id,
                    user_id,
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
                    AND user_id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["transaction_account_id"],
                        user_id,
                    )
                )

            elif operation == OperationType.EXPENSE:
                account_cursor = connection.execute(
                    """
                    UPDATE accounts
                    SET balance_minor = balance_minor - ?
                    WHERE id = ?
                    AND balance_minor >= ?
                    AND user_id = ?
                    """,
                    (
                        row["amount_minor"],
                        row["transaction_account_id"],
                        row["amount_minor"],
                        user_id,
                    )
                )

            else:
                raise ValueError("Неизвестный тип финансовой операции")

            if account_cursor.rowcount == 0:
                raise ValueError("Не удалось скорректировать баланс счёта")
            
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def execute_transfer(self, transfer : Transfer, user_id :int) -> int:
        """Функция выполняет перевод средств с одного счёта на другой"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

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
                    a.currency,
                    a.is_active AS account_is_active,
                    u.is_active AS user_is_active
                FROM accounts AS a
                JOIN users AS u
                ON
                    u.user_id = a.user_id
                WHERE
                    a.id = ?
                AND
                    a.user_id = ?
                """,
                (
                    transfer.source_account_id,
                    user_id,
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
                AND
                    user_id = ?
                """,
                (
                    transfer.dest_account_id,
                    user_id,
                )
            ).fetchone()

            if source_account is None:
                raise ValueError("Счёт отправителя не найден")

            if not bool(source_account["user_is_active"]):
                raise ValueError("Пользователь деактивирован")

            if dest_account is None:
                raise ValueError("Счёт получателя не найден")

            if not bool(source_account["account_is_active"]):
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
                AND  balance_minor >= ?
                AND user_id = ?
                AND is_active = 1
                """,
                (
                    amount_minor,
                    transfer.source_account_id,
                    amount_minor,
                    user_id,
                )
            )

            if source_cursor.rowcount == 0:
                raise ValueError("На счете недостаточно средств")

            dest_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor + ?
                WHERE id = ?
                AND user_id = ?
                AND is_active = 1
                """,
                (
                    amount_minor,
                    transfer.dest_account_id,
                    user_id,
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

    def cancel_transfer(self, transfer_id: int, user_id : int) -> None:
        """Функция выполняет деактивацию перевода между счетами"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")
        
        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if type(transfer_id) is not int:
            raise TypeError("Идентификатор перевода должен быть целочисленным")

        if transfer_id <= 0:
            raise ValueError("Идентификатор перевода должен быть больше нуля")

        connection = get_connection()

        try:
            transfer_row = connection.execute(
                """
                SELECT
                    tr.is_active
                FROM transfers AS tr
                JOIN transactions AS t
                ON
                    t.transfer_id = tr.id
                JOIN accounts AS a
                ON
                    a.id = t.account_id
                WHERE tr.id = ?
                AND a.user_id = ?
                LIMIT 1
                """,
                (
                    transfer_id,
                    user_id,
                )
            ).fetchone()

            if transfer_row is None:
                raise ValueError("Перевод не найден")

            if not bool(transfer_row["is_active"]):
                raise ValueError("Перевод уже деактивирован")

            transaction_in_transfer_row = connection.execute(
                """
                SELECT
                    t.amount_minor,
                    t.is_active,
                    t.account_id
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE t.transfer_id = ?
                AND t.operation = ?
                AND a.user_id = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                    user_id,
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
                    t.amount_minor,
                    t.is_active,
                    t.account_id
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE t.transfer_id = ?
                AND t.operation = ?
                AND a.user_id = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_OUT.value,
                    user_id,
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
                AND operation IN (?,?)
                AND account_id IN (
                    SELECT id
                    FROM accounts
                    WHERE user_id = ?
                )
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                    OperationType.TRANSFER_OUT.value,
                    user_id,
                )
            )

            if transaction_cursor.rowcount != 2:
                raise ValueError("Не удалось деактивировать обе транзакции перевода")

            source_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor + ?
                WHERE id = ?
                AND user_id = ?
                """,
                (
                    transaction_out_transfer_row["amount_minor"],
                    source_acc,
                    user_id,
                )
            )

            if source_acc_cursor.rowcount == 0:
                raise ValueError("Аккаунт не найден в базе")

            dest_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor - ?
                WHERE id = ?
                AND balance_minor >= ?
                AND user_id = ?
                """,
                (
                    transaction_in_transfer_row["amount_minor"],
                    dest_acc,
                    transaction_in_transfer_row["amount_minor"],
                    user_id,
                )
            )

            if dest_acc_cursor.rowcount == 0:
                raise ValueError("На счете недостаточно средств")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def restore_transfer(self, transfer_id : int, user_id : int) -> None:
        """Функция активирует перевод"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")
        
        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if type(transfer_id) is not int:
            raise TypeError("Идентификатор должен быть целочисленным")

        if transfer_id <= 0 :
            raise ValueError("Идентификатор должен быть больше нуля")

        connection = get_connection()

        try:

            transfer_row = connection.execute(
                """
                SELECT
                    tr.is_active
                FROM transfers AS tr
                JOIN transactions AS t
                ON
                    t.transfer_id = tr.id
                JOIN accounts AS a
                ON
                    a.id = t.account_id 
                WHERE tr.id = ?
                AND a.user_id = ?
                LIMIT 1
                """,
                (
                    transfer_id,
                    user_id,
                )
            ).fetchone()

            if transfer_row is None:
                raise ValueError("Перевод с таким идентификатором не найден")

            if bool(transfer_row["is_active"]):
                raise ValueError("Перевод уже активен")

            transaction_out_transfer_row = connection.execute(
                """
                SELECT
                    t.amount_minor,
                    t.is_active,
                    t.account_id
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE t.transfer_id = ?
                AND t.operation = ?
                AND a.user_id = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_OUT.value,
                    user_id,
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
                    t.amount_minor,
                    t.is_active,
                    t.account_id
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE t.transfer_id = ?
                AND t.operation = ?
                AND a.user_id = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                    user_id,
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
                AND operation IN (?,?)
                AND account_id IN (
                    SELECT id
                    FROM accounts
                    WHERE user_id = ?
                )
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                    OperationType.TRANSFER_OUT.value,
                    user_id,
                )
            )

            if transaction_cursor.rowcount != 2:
                raise ValueError("Не удалось активировать обе транзакции перевода")

            source_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor - ?
                WHERE id = ?
                AND balance_minor >= ?
                AND user_id = ?
                """,
                (
                    transaction_out_transfer_row["amount_minor"],
                    source_acc,
                    transaction_out_transfer_row["amount_minor"],
                    user_id,
                )
            )

            if source_acc_cursor.rowcount == 0:
                raise ValueError("На счете недостаточно средств")

            dest_acc_cursor = connection.execute(
                """
                UPDATE accounts
                SET balance_minor = balance_minor + ?
                WHERE id = ?
                AND user_id =?
                """,
                (
                    transaction_in_transfer_row["amount_minor"],
                    dest_acc,
                    user_id,
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