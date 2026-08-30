from transfer import Transfer
from database import get_connection
from transaction import OperationType
from money import from_minor_units
from datetime import date

class TransferRepository:
    """Описание работы с таблицей transfers"""

    def get_transfer_by_id(self, transfer_id : int, user_id : int) -> Transfer:
        """Функция возвращает объект transfer по идентификатору"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")
        
        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if type(transfer_id) is not int:
            raise TypeError("Идентификатор перевода должен быть целочисленным")

        if transfer_id <= 0:
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
                    t.account_id = a.id
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
                raise ValueError("Перевод не найден в базе")

            transfer_out_row = connection.execute(
                """
                SELECT
                    t.account_id,
                    t.action_date,
                    t.amount_minor,
                    t.comment,
                    t.is_active
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE
                    t.transfer_id = ?
                AND
                    t.operation = ?
                AND
                    a.user_id = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_OUT.value,
                    user_id,
                )
            ).fetchone()

            if transfer_out_row is None:
                raise ValueError("Перевод не найден в базе")

            transfer_in_row = connection.execute(
                """
                SELECT
                    t.account_id,
                    t.is_active
                FROM transactions AS t
                JOIN accounts AS a
                ON
                    t.account_id = a.id
                WHERE
                    t.transfer_id = ?
                AND
                    t.operation = ?
                AND
                    a.user_id = ?
                """,
                (
                    transfer_id,
                    OperationType.TRANSFER_IN.value,
                    user_id,
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

    def get_transfers_by_period(self, start_date : date, end_date : date, user_id : int, limit : int = 50, offset : int = 0) -> list[Transfer]:
        """Функция возвращает список объектов Transfer за определенный период"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")
                
        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if not isinstance(start_date,date):
            raise TypeError("Начальная дата должна быть объектом date")

        if not isinstance(end_date,date):
            raise TypeError("Конечная дата должна быть объектом date")

        if start_date > end_date:
            raise ValueError("Дата начала не может быть больше даты конца")

        if type(limit) is not int:
            raise TypeError("Лимит должен быть целочисленным")

        if type(offset) is not int:
            raise TypeError("Смещение должно быть целочисленным")

        if limit <= 0:
            raise ValueError("Лимит должен быть больше нуля")

        if offset < 0:
            raise ValueError("Смещение должно быть больше или равно нулю")

        connection = get_connection()

        transfers : list[Transfer] = []

        try:

            rows = connection.execute(
                """
                SELECT
                    tr.id AS transfer_id,
                    tr.is_active AS transfer_is_active,
                    t_out.action_date AS action_date,
                    t_out.account_id AS source_account_id,
                    t_in.account_id AS dest_account_id,
                    t_out.amount_minor AS amount_minor,
                    t_out.comment AS comment,
                    t_out.is_active AS out_is_active,
                    t_in.is_active AS in_is_active
                FROM transactions AS t_out
                JOIN transactions AS t_in
                    ON t_out.transfer_id = t_in.transfer_id
                JOIN transfers AS tr
                    ON tr.id = t_out.transfer_id
                JOIN accounts AS a_out
                    ON t_out.account_id = a_out.id
                JOIN accounts AS a_in
                    ON t_in.account_id = a_in.id
                WHERE t_out.operation = ?
                AND t_in.operation = ?
                AND t_out.action_date >= ?
                AND t_out.action_date <= ?
                AND a_out.user_id = ?
                AND a_in.user_id = ?
                ORDER BY 
                    t_out.action_date DESC,
                    tr.id DESC
                LIMIT ?
                OFFSET ?
                """,
                (
                    OperationType.TRANSFER_OUT.value,
                    OperationType.TRANSFER_IN.value,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    user_id,
                    user_id,
                    limit,
                    offset,
                )
            ).fetchall()

            for row in rows:

                if bool(row["out_is_active"]) != bool(row["transfer_is_active"]):
                    raise ValueError("Состояние исходящей транзакции не соответствует состоянию перевода")

                if bool(row["in_is_active"]) != bool(row["transfer_is_active"]):
                    raise ValueError("Состояние входящей транзакции не соответствует состоянию перевода")

                transfer = Transfer(
                    action_date= date.fromisoformat(row["action_date"]),
                    source_account_id= row["source_account_id"],
                    dest_account_id= row["dest_account_id"],
                    amount= from_minor_units(row["amount_minor"]),
                    comment= row["comment"],
                    transfer_id= row["transfer_id"],
                    is_active= bool(row["transfer_is_active"])
                )

                transfers.append(transfer)

        finally:
            connection.close()

        return transfers