'''
@author: chaol
'''

from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()
from django.conf import settings
#import eastbourne.shop.filters
urlpatterns = patterns('',
    #(r'^blog/', include('eastbourne.blog.urls')),
    (r'^shop/', include('eastbourne.shop.urls')),
    (r'^blog/', include('eastbourne.blog.urls')),
    (r'^stockists/', include('eastbourne.stockists.urls')),
    (r'^wholesale/', include('eastbourne.shop.wholesaleurls')),
    (r'^states/', include('eastbourne.states_urls')),
    (r'^captcha/', include('captcha.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^admin/filebrowser/', include('filebrowser.urls')), 
    (r'^admin/emails/', 'eastbourne.admin_views.emails_app_index'),
    (r'^admin/shop/order/order(?P<id>.*)/$', "eastbourne.admin_views.order"),
    (r'^admin/shop/order/invoice(?P<id>.*)/$', "eastbourne.admin_views.invoice"),
    (r'^admin/auth/user/(?P<id>.*)/orders/$', "eastbourne.admin_views.order_history"),
    (r'^admin/shop/discountprice/addtocoupon/$','eastbourne.admin_views.addtocoupon'),
    (r'^admin/shop/product/addtocategory/$','eastbourne.admin_views.addtocategory'),
    #(r'^admin/shop/product/addtodiscount/$','eastbourne.admin_views.addtodiscount'),
    (r'^admin/shop/discountprice/category/$',"eastbourne.admin_views.category"),
    (r'^admin/shop/discountprice/delete/$',"eastbourne.admin_views.delete"),
    (r'^admin/shop/productorder/good/$', 'eastbourne.admin_views.productorder'),
    (r'^admin/shop/productorder/good/order(?P<id>.*)/$', 'eastbourne.admin_views.product_order'),
    (r'^admin/shop/orders/myob/$','eastbourne.admin_views.myob'),
    (r'^admin/shop/product/addbycsv/$','eastbourne.admin_views.addbycsv'),
    (r'^admin/website/subscription/sendmail/', 'eastbourne.admin_views.sendmail'),
    (r'^admin/', include(admin.site.urls)),
    #(r'^tinymce/', include('tinymce.urls')),
    (r'^', include('eastbourne.website.urls')),
)
