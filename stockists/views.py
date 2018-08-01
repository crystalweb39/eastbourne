'''
@author: chaol
'''

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import datetime, time
from models import *
from django.db import connection

import pprint, hashlib


from django.core.cache import cache
from django.core.paginator import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout

from django.contrib.auth.models import AnonymousUser

from django.conf import settings

from eastbourne import common


def stockists(request, region):
    t = loader.get_template('stockists.html')
    s = Stockist.objects.filter(region__iexact=region).order_by("state", "suburb")
    openpath = ["stockists", region]
    c = RequestContext(request,common.commonDict({
        'stockists': s,
        'openpath': openpath,
    }, request))
    return HttpResponse(t.render(c))
