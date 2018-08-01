'''
@author: chaol
'''

from django.db import models
from django.contrib.auth.models import User
from eastbourne.website.models import Subscription


class Country(models.Model):
    country = models.CharField(max_length=255)
    shipto = models.BooleanField("Do we ship to this country?")
    def __unicode__(self):
        return self.country
    class Meta:
        verbose_name_plural = "Countries"
class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    def __unicode__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    phone2 = models.CharField(max_length=60, blank=True, null=True)
    fax = models.CharField(max_length=60, blank=True, null=True)
    company = models.CharField(max_length=60, blank=True, null=True)
    tradingas = models.CharField(max_length=60, blank=True, null=True)
    abn = models.CharField(max_length=60, blank=True, null=True)
    subscribe = models.BooleanField(default=False)
    wholesale = models.BooleanField(default=False)
    
    def isStaff(self):
        if self.user.is_staff:
            return True;
        return False
    
    def save(self):
        super(Profile, self).save()
        if self.subscribe:
            Subscription.objects.get_or_create(email=self.user.email,is_wholesale=self.wholesale)
        else:
            try:
                s = Subscription.objects.get(email=self.user.email)
                s.delete()
            except:
                pass
    def __unicode__(self):
        return self.user.username
    class Meta:
        permissions = (
            ("is_wholesaler", "Is a wholesaler"),
        )


class Billing(models.Model):
    profile = models.ForeignKey(Profile)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    address3 = models.CharField(max_length=255, blank=True, null=True)
    suburb = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=60)
    postcode = models.CharField(max_length=60)
    country = models.ForeignKey(Country)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.CharField(max_length=60, blank=True, null=True)
    def __unicode__(self):
        try:
            return "Billing info for "+self.profile.user.username
        except:
            return "Orphaned Billing Data"
    class Meta:
        verbose_name = "Billing Detail"
class Shipping(models.Model):
    profile = models.ForeignKey(Profile)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    address3 = models.CharField(max_length=255, blank=True, null=True)
    suburb = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=60)
    postcode = models.CharField(max_length=60)
    country = models.ForeignKey(Country)
    phone = models.CharField(max_length=60, blank=True, null=True)
    def __unicode__(self):
        try:
            return "Shipping info for "+self.profile.user.username
        except:
            return "Orphaned Shipping Data"
    class Meta:
        verbose_name = "Shipping Detail"


class UserType(models.Model):
    type = models.CharField(max_length=60)
    def __unicode__(self):
        return self.type
class UserLog(models.Model):
    user = models.ForeignKey(User)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.user.username+" "+self.details[:50]+"..."
    def trimDetails(self):
        return self.details[:130]+"..."