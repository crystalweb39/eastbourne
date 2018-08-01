'''
@author: chaol
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^product/(?P<code>.*).html$', 'eastbourne.shop.views.product'),
    (r'^featured.xml$', 'eastbourne.shop.views.featuredxml'), # STEP 1
    (r'^cart.html$', 'eastbourne.shop.views.cart'), # STEP 1
    (r'^details.html$', 'eastbourne.shop.views.checkoutdetails'), # STEP 2
    (r'^confirmdetails.html$', 'eastbourne.shop.views.confirmdetails'), # STEP 3
    (r'^payment.html$', 'eastbourne.shop.views.payment'), # STEP 4
   # (r'^confirm.html$', 'eastbourne.shop.views.confirm'),
    (r'^success(?P<orderid>\d+).html$', 'eastbourne.shop.views.success'), # STEP 5
    (r'^addtocart.json$', 'eastbourne.shop.views.addtocart'),
    (r'^cartsummary.json$', 'eastbourne.shop.views.cartsummary'),
    (r'^calculateshipping.json$', 'eastbourne.shop.views.calculateshippingjson'),
    (r'^getprice.json$','eastbourne.shop.views.getprice'),
    (r'^(?P<code>.*)/(?P<page>.*).html$', 'eastbourne.shop.views.category'),
    (r'^(?P<code>.*)/$', 'eastbourne.shop.views.category'),
    (r'^$', 'eastbourne.shop.views.home'),
    (r'^i/(?P<w>\d+)/(?P<h>\d+)/(?P<crop>\d)/(?P<path>.*)$', 'eastbourne.shop.imageviews.imager'),
    (r'^i/(?P<w>\d+)/(?P<h>\d+)/(?P<path>.*)$', 'eastbourne.shop.imageviews.imager'),
)
