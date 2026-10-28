from database import get_connection
from money import from_minor_units
from datetime import date

connection = get_connection()

start_date = date(2026, 10, 1)

sum = 0

rows = connection.execute(
    """
    SELECT
        operation,
        amount_minor
    FROM transactions
    WHERE
        category = "Еда"
    AND
        action_date >= ?
    """,
    (
        start_date.isoformat(),
    )
).fetchall()

for row in rows:

    expense = from_minor_units(row["amount_minor"])

    text = f"{row["operation"]}: {expense} KZT"

    if row["operation"] == "Расход":

        sum += expense

    else:

        sum -= expense

    print(text)

print(f"Суммарный расход: {sum} KZT")

