'''
@author: chaol
'''

from django.contrib import admin
from django.contrib.contenttypes import generic

from models import *

class StockistAdmin(admin.ModelAdmin):
    list_display = ('name', 'suburb', 'region')
    list_filter = ('region',)

admin.site.register(Stockist, StockistAdmin)