'''
@author: chaol
'''

from django.db import models

class Stockist(models.Model):
    suburb = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    region = models.CharField(max_length=50, choices=(("AUSTRALIA", "AUSTRALIA"), ("INTERNATIONAL","INTERNATIONAL")))
    def __unicode__(self):
        return self.name
#