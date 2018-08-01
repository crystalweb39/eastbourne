'''
@author: chaol
'''

from django.contrib import admin
from django.contrib.contenttypes import generic

from models import *

class CountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'shipto',)
    list_filter = ('shipto',)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country',)
    list_filter = ('country',)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp','trimDetails')
    search_fields = ('user__username','details')

class ShippingInline(admin.StackedInline):
    max_num = 1   
    model = Shipping
    
class ShippingAdmin(admin.ModelAdmin):
    list_display=('profile','company','state','postcode','country')
class BillingInline(admin.StackedInline):
    max_num = 1
    model = Billing
class ProfileAdmin(admin.ModelAdmin):
    list_filter = ('wholesale', 'subscribe','company')
    list_display=('user', 'wholesale','company')
    inlines = [
        ShippingInline,
        BillingInline,
    ]
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(UserType)
admin.site.register(UserLog, UserLogAdmin)
admin.site.register(Shipping,ShippingAdmin)
admin.site.register(Billing)