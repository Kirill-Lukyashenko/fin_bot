from user import User
from database import get_connection

class UserRepository:
    """Описание работы с таблицей users"""

    def add_user(self, user : User) -> int:
        """Функция добавляет нового пользователя"""

        if not isinstance(user, User):
            raise TypeError("Пользователь должен быть объектом User")

        if user.user_id is not None:
            raise ValueError("Данный пользователь уже имеет идентификатор")

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                INSERT INTO users (
                    telegram_user_id,
                    is_active
                )
                VALUES (?,?)
                """,
                (
                    user.telegram_user_id,
                    int(user.is_active),
                )
            )

            connection.commit()

            user.user_id = cursor.lastrowid

            return user.user_id


        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()


    def get_user_by_id(self, user_id : int) -> User | None:
        """Функция возвращает объект User по внутреннему идентификатору"""

        if type(user_id) is not int:
            raise TypeError("Идентификатор пользователя должен быть целочисленным")

        if user_id <= 0:
            raise ValueError("Значение идентификатора пользователя должно быть больше нуля")

        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    telegram_user_id,
                    is_active
                FROM users
                WHERE user_id = ?
                """,
                (
                    user_id,
                )
            ).fetchone()

            if row is None:
                return None

        finally:
            connection.close()

        user = User(
            telegram_user_id= row["telegram_user_id"],
            is_active= bool(row["is_active"]),
            user_id= user_id
        )
        
        return user

    def get_user_by_telegram_id(self, telegram_user_id : int) -> User | None:
        """Функция возвращает объект User по Telegram-идентификатору"""

        if type(telegram_user_id) is not int:
            raise TypeError("Идентификатор пользователя Telegram должен быть целочисленным")

        if telegram_user_id <= 0:
            raise ValueError("Идентификатор пользователя Telegram должен быть больше нуля")

        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    user_id,
                    is_active
                FROM users
                WHERE telegram_user_id = ?
                """,
                (
                    telegram_user_id,
                )
            ).fetchone()

            if row is None:
                return None

        finally:
            connection.close()


        return User(
            telegram_user_id= telegram_user_id,
            user_id= row["user_id"],
            is_active= bool(row["is_active"])
        )

    def update_user_state(self, user: User) -> None:
        """Функция обновляет состояние пользователя"""

        if not isinstance(user, User):
            raise TypeError("Пользователь должен быть объектом User")

        if user.user_id is None:
            raise ValueError("Нельзя обновить пользователя без внутреннего идентификатора")

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                UPDATE users
                SET
                    is_active = ?
                WHERE user_id = ?
                """,
                (
                    int(user.is_active),
                    user.user_id,
                )
            )

            if cursor.rowcount == 0:
                raise ValueError("Пользователь с таким идентификатором не существует")

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        