'''
@author: chaol
'''

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
import datetime, time, math
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

from eastbourne.userprofile.models import *

from django.core.paginator import Paginator

from forms import *

def home(request, offset=1):
    t = loader.get_template('blog_index.html')
    offset = int(offset)
    perpage = settings.BLOG_POSTS_PER_PAGE
    start = offset*perpage
    end = start+perpage
    
#    postcount = BlogPost.objects.select_related().filter(status__display_to_user=True, publishdate__lte=datetime.datetime.now()).order_by("-publishdate").count()
    
    blogposts = BlogPost.objects.select_related().filter(status__display_to_user=True, publishdate__lte=datetime.datetime.now()).order_by("-publishdate")
    
    p = Paginator(blogposts, perpage)
    
    page = p.page(offset)
    
    #return HttpResponse("")
    c = RequestContext(request,common.commonDict({
        'blogposts': page.object_list,
        "openpath": ["blog"],
        "page": page,
    }, request))
    return HttpResponse(t.render(c))

def post(request, code):
    t = loader.get_template('blogpost.html')
    #return HttpResponse(str(dir(Product.objects.get(code=code))))
    blogpost = BlogPost.objects.get(slug=code)
    rp = request.POST.copy()
    messages = []
    if rp:
        form = CommentForm(rp)
    else:
        form = CommentForm()
    if form.is_valid(): # All validation rules pass
        c = Comment(post=blogpost, name=form.cleaned_data["name"], email=form.cleaned_data["email"], comment=form.cleaned_data["comment"], status=CommentStatus.objects.get(status="Published"))
        c.save()
        messages.append("Thanks for your comment")  
        return HttpResponseRedirect(blogpost.getURL())
    c = RequestContext(request,common.commonDict({
        'blogpost': blogpost,
        'form': form,
        'messages': messages,
        "openpath": ["blog"],
    }, request))
    return HttpResponse(t.render(c))