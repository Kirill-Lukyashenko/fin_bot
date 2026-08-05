from decimal import Decimal

from money import from_minor_units, to_minor_units


amount = Decimal("6032.53")

amount_minor = to_minor_units(amount)
restored_amount = from_minor_units(amount_minor)

print(amount_minor)
print(restored_amount)

assert amount_minor == 603253
assert restored_amount == Decimal("6032.53")

print("Функции преобразования денег работают правильно")