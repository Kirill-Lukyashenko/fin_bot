from transfer import Transfer
from database import get_connection
from transaction import OperationType
from money import from_minor_units
from datetime import date

class TransferRepository:
    """Описание работы с таблицей transfers"""

    def get_transfer_by_id(self, transfer_id : int) -> Transfer:
        """Функция возвращает объект transfer по идентификатору"""

        if type(transfer_id) is not int:
            raise TypeError("Идентификатор перевода должен быть целочисленным")

        if transfer_id <= 0:
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
                raise ValueError("Перевод не найден в базе")

            transfer_out_row = connection.execute(
                """
                SELECT
                    account_id,
                    action_date,
                    amount_minor,
                    comment,
                    is_active
                FROM transactions
                WHERE
                    transfer_id = ?
                AND
                    operation = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_OUT.value,
                )
            ).fetchone()

            if transfer_out_row is None:
                raise ValueError("Перевод не найден в базе")

            transfer_in_row = connection.execute(
                """
                SELECT
                    account_id,
                    is_active
                FROM transactions
                WHERE
                    transfer_id = ?
                AND
                    operation = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                )
            ).fetchone()

            if transfer_in_row is None:
                raise ValueError("Перевод не найден в базе")

            transfer_is_active = bool(transfer_row["is_active"])

            if bool(transfer_out_row["is_active"]) != transfer_is_active:
                raise ValueError("Состояние исходящей транзакции не соответствует состоянию перевода")

            if bool(transfer_in_row["is_active"]) != transfer_is_active:
                raise ValueError("Состояние входящей транзакции не соответствует состоянию перевода")

            transfer = Transfer(
                action_date= date.fromisoformat(transfer_out_row["action_date"]),
                source_account_id= transfer_out_row["account_id"],
                dest_account_id= transfer_in_row["account_id"],
                amount= from_minor_units(transfer_out_row["amount_minor"]),
                comment= transfer_out_row["comment"],
                transfer_id= transfer_id,
                is_active= transfer_is_active
            )

        finally:
            connection.close()

        return transfer