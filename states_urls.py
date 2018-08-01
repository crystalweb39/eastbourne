'''
@author: chaol
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
        (r'^order/$','eastbourne.dashboard_helper.order_statistics'),
        (r'^sale/$','eastbourne.dashboard_helper.sale_statistics'),
        (r'^datalist/$','eastbourne.dashboard_helper.build_datalist'),
        (r'^analytics/$','eastbourne.dashboard_helper.analytics'),
)
