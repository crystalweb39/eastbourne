'''
@author: chaol
'''

def formatCurrency(amount):
    try:
        p = str(amount).split(".")
        if len(p[1]) < 2:
            p[1] = str(p[1])+str(0)
        elif len(p[1]) > 2:
            p[1] = str(p[1][:2])
        price = ".".join(p)
        return price
    except:
        return amount
