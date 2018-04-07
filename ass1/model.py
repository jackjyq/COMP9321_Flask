import copy

database = {}
template = {'order': None, 
            'cost': None, 
            'coffee': None, 
            'additions': None, 
            'status': {
                'paymentStatus': "notPayed",
                'releaseStatus': "open",
                'drinkStatus': "pending"
                }, 
            'payment': {
                'type': None, 
                'amount': None, 
                'cardNumber': None, 
                'name': None, 
                'expireDate': None
                }
            }



# check the attribute's format
def isValidOrder(order):
    try:
        if (int(order) < 0):
            return False
    except ValueError:
            return False
    return True


def isValidMoney(Money):
    try:
        if (float(Money) < 0):
            return False
    except ValueError:
            return False
    return True

# other database helper funtions
def existOrderID(order):
    if int(order) in database.keys():
        return True
    else:
        return False

def existAttribute(key, dictionary):
    if key in dictionary.keys():
        return True
    else:
        return False
