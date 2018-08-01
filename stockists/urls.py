'''
@author: chaol
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<region>.*).html$', 'eastbourne.stockists.views.stockists'),
)
