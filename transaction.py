from decimal import Decimal
from account import Account
from datetime import date

class Transaction:

    def __init__(self,
                 action_date : date,
                 amount : str | Decimal,
                 operation : str,
                 category : str,
                 account : Account,
                 comment : str,
                 transaction_id : int | None = None
                 ):
        self.action_date = action_date
        self.amount = Decimal(amount)
        self.operation = operation
        self.category = category
        self.account = account
        self.comment = comment
        self.transaction_id = transaction_id