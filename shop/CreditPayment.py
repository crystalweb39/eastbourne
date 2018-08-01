'''
@author: chaol
'''
class CreditPayment:
    def __init__(self):
        self.type = "VISA" # VISA, AMEX, DINERS, BANKCARD
        self.number = ""
        self.expiry = ""
        self.name = ""
        self.CCV = ""
        self.amount = 0.0
        self.status = False
        self.error = False
        self.errormsg = ""
    def cleanNumber(self):
        self.number = self.number.replace(" ", "")
        self.number = self.number.replace("-", "")
        self.number = int(self.number)
    def check_number(self):
        """
        Luhn credit card number check
        """
        digits = self.number
        _sum = 0
        alt = False
        ix = []
        for x in str(digits):
            ix.append(int(x))
        for d in reversed(ix):
            assert 0 <= d <= 9
            if alt:
                d *= 2
                if d > 9:
                    d -= 9
            _sum += d
            alt = not alt
        return (_sum % 10) == 0
    def process(self):
        self.cleanNumber()
        if not self.check_number():
            self.status = False
            self.error = True
            self.errormsg = "Credit Card number failed validation"
            return False
        if self.amount > 0:
            self.error = False
            self.status = True
            return True
        else:
            self.error = True
            self.status = False
            self.errormsg = "Amount must be greater than $0"
            return False