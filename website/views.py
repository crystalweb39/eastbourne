'''
@author: chaol
'''

from django.template import Context, loader, RequestContext
from django.http import HttpResponse
from django.core.validators import email_re
import datetime, time
from models import *
from eastbourne.shop.models import *
from django.db import connection
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout
from eastbourne import common
from eastbourne.userprofile.models import *
from eastbourne.website.models import *
from django.http import HttpResponseRedirect

def home(request):
    t = loader.get_template('index.html')
    coupon = request.session.get('coupon','')
    coupons = Coupon.objects.all()
    if coupon:
        validate = [True if x.checkCode(coupon) else False for x in coupons]
        if validate.count(False) == len(coupons):
            request.session['coupon'] = ''
            order_id = request.session.get('order_id',None)
            if order_id:
                order = Order.objects.get(id=order_id)
                po = order.productorder_set.all()
                for x in po:
                    x.price = x.product.getTaxFreePrice(x.size,request.user.is_active,'')
                    x.save()
        else:
            request.session['coupon'] = coupon
    #return HttpResponse(str(dir(getCategories()[0])))
    c = RequestContext(request,common.commonDict({"openpath": ["home"], }, request))
    #return HttpResponse(common.commonDict({"openpath": ["home"],}, request)["products"])
    #raise Exception({'coupon':coupon,'coupon2':validate,'dict':common.commonDict({"openpath": ["home"], }, request)})
    return HttpResponse(t.render(c))

def is_valid_email(email):
    return True if email_re.match(email) else False

def subscribe(request):
    data = {"openpath": ["home"],}
    if is_valid_email(request.POST.get("email")):
        try:
            o = User.objects.get(email=request.POST.get("email"))
            if Profile.objects.get(user=o.id).wholesale:
                
                s, created = Subscription.objects.get_or_create(email=request.POST.get("email"), defaults={"is_wholesale": True, "ip": request.META["REMOTE_ADDR"]})
            else:
                s, created = Subscription.objects.get_or_create(email=request.POST.get("email"), defaults={"is_wholesale": False, "ip": request.META["REMOTE_ADDR"]})
            t = loader.get_template('subscribe.html')
            if created:
                data["error"] = 0
                data["message"] = "Thanks for subscribing to our newsletter."
            else:
                data["error"] = 1
                data["message"] = "There was an error, perhaps you're already subscribed?"
        except:
            s, created = Subscription.objects.get_or_create(email=request.POST.get("email"), defaults={"is_wholesale": False, "ip": request.META["REMOTE_ADDR"]})
            t = loader.get_template('subscribe.html')
            if created:
                data["error"] = 0
                data["message"] = "Thanks for subscribing to our newsletter."
            else:
                data["error"] = 1
                data["message"] = "There was an error, perhaps you're already subscribed?"
    else:
        data["error"] = 1
        data["message"] = "Please use a valid email address"
    c = RequestContext(request,common.commonDict(data, request))
    return HttpResponse(str(data))

def coupon(request):
    rp = request.GET.copy()
    data = {}
    if rp:
        coupon = rp.get('coupon','')
        status = rp.get('status','')
        if status == 'true':
            validate = False
            coupons = Coupon.objects.all()
            result = [True if x.checkCode(coupon) else False for x in coupons]
            validate = True if result.count(True) != 0 else False
            if validate:
                order_id = request.session.get('order_id',None)
                if order_id:
                    order = Order.objects.get(id=order_id)
                    po = order.productorder_set.all()
                    for x in po:
                        x.price = x.product.getTaxFreePrice(x.size,request.user.is_active,coupon)
                        x.save()
                request.session['coupon'] = coupon
                data['error'] = 0
                data['message'] = 'Congratulations! It is a valid coupon. Enjoy shopping!'
            else:
                data['error'] = 1
                data['message'] = 'There was an error, perhaps your coupon code is not correct or it is expired.'
        else:
            request.session['coupon'] = ''
            order_id = request.session.get('order_id',None)
            if order_id:
                order = Order.objects.get(id=order_id)
                po = order.productorder_set.all()
                for x in po:
                    x.price = x.product.getTaxFreePrice(x.size,request.user.is_active,'')
                    x.save()
            data['error'] = 3
            data['message'] = ''
    #raise Exception({'request':request.session['coupon']})
    return HttpResponse(str(data))

def catchall(request, path):
    try:
        document = MiscPage.objects.get(path=path, status__display_to_user=True)
        t = loader.get_template('catchall.html')
        c = RequestContext(request,common.commonDict({"openpath": ["home"],"document": document,}, request))
        return HttpResponse(t.render(c))
    except Exception, e:
        #TODO make 404
        return HttpResponse("Couldn't find the file you were looking for")
def about(request):
    
    try:
        document = MiscPage.objects.get(path="about.html", status__display_to_user=True)
        t = loader.get_template('catchall.html')
        c = RequestContext(request,common.commonDict({"openpath": ["about.html"],"document": document,}, request))
        return HttpResponse(t.render(c))
    except Exception, e:
        #TODO make 404
        return HttpResponse("Couldn't find the file you were looking for")
    
def readnotification(request):
    rp = request.GET.copy()
    id = rp.get('id',0)
    email = rp.get('email',0)
    es = EmailStatus.objects.filter(subscribe__id=id, email__id=email)
    if es:
        es = es[0]
        es.read = True
        es.save()
    return HttpResponseRedirect('/media/assets/right.png')

    
