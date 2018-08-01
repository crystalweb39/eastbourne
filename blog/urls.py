'''
@author: chaol
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'eastbourne.blog.views.home'),
    (r'^archive(?P<offset>.*).html$', 'eastbourne.blog.views.home'),
    (r'^(?P<code>.*).html$', 'eastbourne.blog.views.post'),
)
