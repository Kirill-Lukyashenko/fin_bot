from account import Account
from transaction import Transaction, OperationType
from datetime import date

kaspi = Account(1,"KASPI","CARD","GOLD","4084","0.0","KZT",None,True)
tr1 = Transaction(date(2026,8,3),"10.00",OperationType.INCOME,"Зарплата",kaspi,"Получил ЗП",None,False)

print(kaspi.check_state())
print(tr1.check_state())