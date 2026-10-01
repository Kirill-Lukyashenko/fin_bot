from obligation import Obligation, ObligationType, CurrencyType
from database import get_connection
from money import from_minor_units, to_minor_units
from datetime import date


class ObligationRepository:
    """Описание работы с таблицей obligations"""

    def add_obligation_in_transaction(self, obligation : Obligation, connection, user_id : int) -> int:
        """Добавляет обязательство в рамках внешней транзакции"""

        if not isinstance(obligation, Obligation):
            raise TypeError("Обязательство должно быть объектом Obligation")

        if obligation.obligation_id is not None:
            raise ValueError("Данное обязательство уже имеет идентификатор")

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if obligation.user_id != user_id:
            raise ValueError("Обязательство не принадлежит указанному пользователю")

        amount_minor = to_minor_units(obligation.amount)

        remaining_amount_minor = to_minor_units(obligation.remaining_amount)

        cursor = connection.execute(
            """
            INSERT INTO obligations(
                    user_id,
                    counterparty,
                    obligation_type,
                    amount_minor,
                    remaining_amount_minor,
                    currency,
                    start_date,
                    end_date,
                    is_active,
                    comment
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                obligation.user_id,
                obligation.counterparty,
                obligation.obligation_type.value,
                amount_minor,
                remaining_amount_minor,
                obligation.currency.value,
                obligation.start_date.isoformat(),
                (
                    obligation.end_date.isoformat()
                    if obligation.end_date is not None
                    else None
                ),
                int(obligation.is_active),
                obligation.comment,
            )
        )

        obligation.obligation_id = cursor.lastrowid
        
        return obligation.obligation_id

    def add_obligation(self, obligation : Obligation, user_id : int) -> int:
        """Функция добавляет новое обязательство в базу"""

        connection = get_connection()

        try:

            obligation_id = self.add_obligation_in_transaction(obligation, connection, user_id)

            connection.commit()

            return obligation_id

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_obligation_by_id(self, obligation_id : int, user_id : int) -> Obligation | None:
        """Функция восстанваливает объект Obligation из БД по идентификатору"""

        if type(obligation_id) is not int:
            raise TypeError("Идентификатор обязательства должен быть целочисленным")

        if obligation_id <=0:
            raise ValueError("Идентификатор обязательства должен быть больше нуля")

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <=0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        connection = get_connection()

        try:

            row = connection.execute(
                """
                SELECT
                    id,
                    user_id,
                    counterparty,
                    obligation_type,
                    amount_minor,
                    remaining_amount_minor,
                    currency,
                    start_date,
                    end_date,
                    comment,
                    is_active
                FROM obligations
                WHERE
                    id = ?
                AND
                    user_id = ?
                """,
                (
                    obligation_id,
                    user_id,
                )
            ).fetchone()

        finally:

            connection.close()

        if row is None:
            return None

        return Obligation(
            obligation_id= row["id"],
            user_id= row["user_id"],
            counterparty= row["counterparty"],
            obligation_type= ObligationType(row["obligation_type"]),
            amount= from_minor_units(row["amount_minor"]),
            remaining_amount= from_minor_units(row["remaining_amount_minor"]),
            currency= CurrencyType(row["currency"]),
            start_date= date.fromisoformat(row["start_date"]),
            end_date= (
                date.fromisoformat(row["end_date"])
                if row["end_date"] is not None
                else None 
            ),
            comment= row["comment"],
            is_active= bool(row["is_active"])
        )

    def get_obligations_by_user_id(self, user_id : int) -> list[Obligation] :
        """Функция возвращает список активных обязательств у конкретного пользователя"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        connection = get_connection()

        try:

            rows = connection.execute(
                """
                SELECT
                    id,
                    user_id,
                    counterparty,
                    obligation_type,
                    amount_minor,
                    remaining_amount_minor,
                    currency,
                    start_date,
                    end_date,
                    comment,
                    is_active
                FROM obligations
                WHERE
                    user_id = ?
                AND
                    is_active = 1
                """,
                (
                    user_id,
                )
            ).fetchall()

        finally:

            connection.close()

        obligations = []

        for row in rows:

            obligation = Obligation(
                obligation_id= row["id"],
                user_id= row["user_id"],
                counterparty= row["counterparty"],
                obligation_type= ObligationType(row["obligation_type"]),
                amount= from_minor_units(row["amount_minor"]),
                remaining_amount= from_minor_units(row["remaining_amount_minor"]),
                currency= CurrencyType(row["currency"]),
                start_date= date.fromisoformat(row["start_date"]),
                end_date= (
                    date.fromisoformat(row["end_date"])
                    if row["end_date"] is not None
                    else None
                ),
                comment= row["comment"],
                is_active= bool(row["is_active"])
            )

            obligations.append(obligation)

        return obligations

    def update_obligation(self, obligation : Obligation, user_id : int) -> None:
        """Функция изменяет данные существующего обязательства"""

        if not isinstance(obligation, Obligation):
            raise TypeError("Обязательство должно быть объектом Obligation")

        if obligation.obligation_id is None:
            raise ValueError("Нельзя обновить обязательство без идентификатора")

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        if obligation.user_id != user_id:
            raise ValueError("Обязательство не принадлежит указанному пользователю")

        amount_minor = to_minor_units(obligation.amount)

        remaining_amount_minor = to_minor_units(obligation.remaining_amount)

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                UPDATE obligations
                SET
                    counterparty = ?,
                    obligation_type = ?,
                    amount_minor = ?,
                    remaining_amount_minor = ?,
                    currency = ?,
                    start_date = ?,
                    end_date = ?,
                    comment = ?,
                    is_active = ?
                WHERE
                    id = ?
                AND
                    user_id = ?
                """,
                (
                    obligation.counterparty,
                    obligation.obligation_type.value,
                    amount_minor,
                    remaining_amount_minor,
                    obligation.currency.value,
                    obligation.start_date.isoformat(),
                    (
                        obligation.end_date.isoformat()
                        if obligation.end_date is not None
                        else None
                    ),
                    obligation.comment,
                    int(obligation.is_active),
                    obligation.obligation_id,
                    user_id
                )
            )

            if cursor.rowcount == 0:
                raise ValueError("Записи с таким идентификатором не существует")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def deactivate_obligation(self, obligation_id : int, user_id : int) -> None:
        """Функция деактивирует обязательство"""

        if type(obligation_id) is not int:
            raise TypeError("Идентификатор обязательства должен быть целочисленным")

        if obligation_id <= 0:
            raise ValueError("Идентификатор обязательства должен быть больше нуля")

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Идентификатор пользователя должен быть больше нуля")

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                UPDATE obligations
                SET
                    is_active = 0
                WHERE
                    id = ?
                AND
                    user_id = ?
                AND
                    is_active = 1
                """,
                (
                    obligation_id,
                    user_id,
                )
            )

            if cursor.rowcount == 0:
                raise ValueError("Активного обязательства с таким идентификатором не существует")

            connection.commit()

        except Exception:

            connection.rollback()
            raise

        finally:

            connection.close()