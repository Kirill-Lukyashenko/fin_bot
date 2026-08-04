from account import Account
from transaction import Transaction, OperationType
from datetime import date

kaspi = Account(1,"Kaspi","Карта","Kaspi gold", "4084","0.0","KZT", None)

income = Transaction(date(2026,8,4),"5000.00",OperationType.INCOME, "Зарплата", kaspi, "Получил зпшку")
expense = Transaction(date(2026,8,4),"2000.00",OperationType.EXPENSE, "Продукты", kaspi, "Закупился в магазине")