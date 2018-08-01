'''
@author: chaol
'''
from eastbourne.shop.models import *
from eastbourne.website.models import *
from eastbourne.blog.models import *
from eastbourne.website.models import Subscription
from random import *
from django.db.models import Q

from django.conf import settings

from eastbourne.shop.shipping.AustraliaPostDomestic import AustraliaPostDomestic
from eastbourne.shop.shipping.AustraliaPostInternational import AustraliaPostInternational


import hashlib
import datetime
def split_list(l, length):
    """
    Takes a list and splits into a list of lists of size X
    """
    if not l:
        return []
    ret = []
    cur = []
    rowdone = False
    l = list(l)
    for x in l:
        cur.append(x)
        if len(cur) == length:
            ret.append(cur)
            cur = []
            rowdone = True
        else:
            rowdone = False
    if not rowdone:
        ret.append(cur)
    return ret

def getNewsItems():
    return NewsItem.objects.filter(publish_date__lte=datetime.datetime.now(), status__display_to_user=True).order_by("-publish_date")[:4]
def getCategories():
    return Categories.objects.select_related().filter(is_active=True, parent__isnull=True).order_by("-priority","name")
def getFeaturedProducts(request):
    # Lets select products based on the type of customer we're working with
    products = Product.objects.distinct().filter(sites__pk=settings.SITE_ID).filter(category_now__is_active=True, status__display_to_user=True, status__status__iexact = "featured")
    if request.user.is_active:
        products = products.filter(wholesale_price__gt=0)
    else:
        products = products.filter(price__gt=0)
    p = list(products)
    shuffle(p)
    return p

def getTopFeatured(request):
    
    products = Product.objects.distinct().filter(sites__pk=settings.SITE_ID).filter(category_now__is_active=True, status__display_to_user=True, status__status__iexact = "top featured")
    if request.user.is_active:
        products = products.filter(wholesale_price__gt=0)
    else:
        products = products.filter(price__gt=0)
    p = list(products)
    shuffle(p)
    return p

def getLatestBlogPost():
    return BlogPost.objects.select_related().filter(status__display_to_user=True, publishdate__lte=datetime.datetime.now()).order_by("-publishdate")[0]
def getStrings():
    s = Strings.objects.all()
    st = {}
    for x in s:
        st[x.identifier.replace(".", "_")] = x.text
    return st
def isSubscriber(request):
    if not request.user.is_active:
        return False
    else:
        try:
            Subscription.objects.get(email=request.user.email.lower())
            return True
        except Exception, e:
            return False
def commonDict(d, request):
    
    news = getNewsItems()
    products = getFeaturedProducts(request)
    top = getTopFeatured(request)
    data = {    'usr':None,
                'newsItems': news,
                'newsItem': news[0],
                'products': products,
                'categories': getCategories(),
                'latestBlogPost': getLatestBlogPost(),
                'strings': getStrings(),
                'is_subscriber': isSubscriber(request),
                
                
              }
    data['coupon'] = request.session.get("coupon", '')
    
    if len(products) > 0:
        data['featuredproduct'] = products[-1]
    
    if top:
        data['products'] = top + products

    if request.user and request.user.is_active:
        data['usr'] = request.user
 
    if request.session.get("order_id", None):
        try:
            data["order"] = Order.objects.get(pk=request.session.get("order_id", 0))
        except:
            del request.session['order_id']
    data.update(d)
    return data
def formatCurrency(amount):
    try:
        p = str(amount).split(".")
        if len(p[1]) < 2:
            p[1] = str(p[1])+str(0)
        elif len(p[1]) > 2:
            p[1] = str(p[1][:2])
        price = ".".join(p)
        return price
    except:
        return amount
    
def getResponse(order,action='set',token='',payerid=''):
    Username = settings.USERNAME
    Password = settings.PASSWORD
    Signature = settings.SIGNATURE
    token = token
    payerid = payerid
    tokens = {}
    domain = settings.DOMAIN
    credientials = {'USER':Username,
        'PWD':Password,
        'VERSION': '52.0',
        'SIGNATURE':Signature}

    if action == 'set':
        actions = {'METHOD'        : 'SetExpressCheckout',
                   'PAYMENTACTION' : 'Sale',
                   'AMT'           : order.getTotalCharged(),
                   'CURRENCYCODE'  : 'AUD',
                   'RETURNURL'     : 'http://%s/shop/success%s.html' %(domain,order.id),
                   'CANCELURL'     : 'http://%s/shop/cart.html' % domain,
                   'NOSHIPPING'    : '1'
                       }
    else:
        actions = {'METHOD'        : 'DoExpressCheckoutPayment',
                   'TOKEN'         : token,
                   'PAYMENTACTION' : 'Sale',
                   'CURRENCYCODE'  : 'AUD',
                   'AMT'           : order.getTotalCharged(),
                   'PAYERID'       : payerid
                       }
    cres = urllib.urlencode(credientials)
    acts = urllib.urlencode(actions)
    params = "%s&%s" %(cres,acts)
    #print params 
    response = urllib.urlopen("https://api-3t.paypal.com/nvp", params)
    uri_response = urllib.unquote(response.read())
        
        #split up the response
    for token in uri_response.split('&'):
        tokens[str(token.split("=")[0])] = str(token.split("=")[1])
    return tokens
    