from django.conf import settings
import hashlib
def generateAmountHash(amount):
    return hashlib.md5(settings.SECRET_KEY+str(float(amount))).hexdigest()