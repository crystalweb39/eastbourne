'''
@author: chaol
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'eastbourne.website.views.home'),
    #(r'^subscribe.html$', 'website.views.subscribe'),
    (r'^subscribe.json$', 'eastbourne.website.views.subscribe'),
    (r'^coupon.json$','eastbourne.website.views.coupon'),
    (r'^about.html', 'eastbourne.website.views.about'),
    (r'^reademail','eastbourne.website.views.readnotification'),
    (r'^(?P<path>.*)$', 'eastbourne.website.views.catchall'),
)
