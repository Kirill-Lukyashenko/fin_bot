from obligation import Obligation, ObligationType, CurrencyType
from database import get_connection
from money import from_minor_units, to_minor_units
from datetime import date

class ObligationRepository:
    """Описание работы с таблицей obligations"""

    def add_obligation(self, obligation : Obligation) -> int:
        """Функция добавляет новое обязательство в базу"""

        if not isinstance(obligation, Obligation):
            raise TypeError("Должен быть передан объект obligation")

        if obligation.obligation_id is not None:
            raise ValueError("Данное обязательство уже имеет идентификатор")

        amount_minor = to_minor_units(obligation.amount)

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                INSERT INTO obligations (
                    user_id,
                    obligation_type,
                    amount_minor,
                    currency,
                    start_date,
                    end_date,
                    is_active,
                    comment
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    obligation.user_id,
                    obligation.obligation_type.value,
                    amount_minor,
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

            connection.commit()

            obligation.obligation_id = cursor.lastrowid

            return obligation.obligation_id

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_obligation_by_id(self, obligation_id : int, user_id : int) -> Obligation | None:
        """Функция востанваливает объект Obligation из БД по идентификатору"""

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
                    obligation_type,
                    amount_minor,
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
            obligation_type= ObligationType(row["obligation_type"]),
            amount= from_minor_units(row["amount_minor"]),
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