'''
@author: chaol
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'eastbourne.shop.wholesaleviews.login'),
    (r'^register.html$', 'eastbourne.shop.wholesaleviews.register'),
    (r'^registered.html$', 'eastbourne.shop.wholesaleviews.registered'),
    (r'^login.html$', 'eastbourne.shop.wholesaleviews.login'),
    (r'^orders.html$', 'eastbourne.shop.wholesaleviews.orders'),
    (r'^order(?P<id>\d+).html$', 'eastbourne.shop.wholesaleviews.order'),
    (r'^profile.html$', 'eastbourne.shop.wholesaleviews.profile'),
    (r'^shipping.html$', 'eastbourne.shop.wholesaleviews.shipping'),
    (r'^logout.html$', 'eastbourne.shop.wholesaleviews.logout'),
    (r'^forgotpassword.html$', 'eastbourne.shop.wholesaleviews.forgotpassword'),
)
