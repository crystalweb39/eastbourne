'''
@author: chaol
'''

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import datetime, time
from models import *
from django.db import connection
import httplib, urllib
from django.db.models import Q

import pprint, hashlib

from django.core.mail import send_mail

from django.core.cache import cache
from django.core.paginator import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout

from django.contrib.auth.models import AnonymousUser

from django.conf import settings

from eastbourne import common

from eastbourne.userprofile.models import *

from ShopLogging import Log

from eway import config
from eway.client import EwayPaymentClient
from eway.fields import Customer, CreditCard
from CreditPayment import CreditPayment
from decimal import Decimal

from django.core.mail import EmailMultiAlternatives

from forms import *

from eastbourne.shop import generateAmountHash
#from eastbourne.common import gcalculateshipping
from django.utils import simplejson

def home(request):
    return HttpResponseRedirect("/")

def product(request, code):
    t = loader.get_template('product.html')
    product = Product.objects.get(code=code)
    related = product.getRelatedProducts(request.user.is_active)

    if not request.user.is_active:
        quantities = range(product.minimum_quantity, product.maximum_quantity+1)
    else:
        quantities = range(product.minimum_quantity_wholesale, product.maximum_quantity_wholesale+1)
    c = RequestContext(request,common.commonDict({
        'product': product,
        'quantities': quantities,
        'related': related,
    }, request))

    
    return HttpResponse(t.render(c))
def category(request, code, page=1):
    request.session["lastpage"] = request.path
    page = int(page)
    t = loader.get_template('category.html')
    cat = Categories.objects.select_related().get(slug=code)
    products = cat.product_set.distinct().filter(status__display_to_user=True, sites__pk=settings.SITE_ID).order_by("title")
    if request.user.is_active:
        products = products.filter(wholesale_price__gt=0)
    else:
        products = products.filter(price__gt=0)
    p = Paginator(list(products), settings.PRODUCTS_PER_PAGE)
    try:
        pagination = {"paginator": p, "page": p.page(page), "pagenumber": page}
        products = p.page(page).object_list
    except EmptyPage, e:
        return HttpResponseRedirect(cat.getUrl())
    openpath = ["shop"]
    if cat.parent:
        openpath.append(cat.parent.slug)
    openpath.append(code)
    c = RequestContext(request,common.commonDict({
        'category': cat,
        'products': common.split_list(products, 3),
        'page': pagination,
        "openpath": openpath,
        }, request))
    return HttpResponse(t.render(c))
def featuredxml(request):
    t = loader.get_template('featured.xml')
        
    # Lets select products based on the type of customer we're working with
    c = RequestContext(request,common.commonDict({"openpath": ["home"]}, request))
    return HttpResponse(t.render(c), mimetype="application/xml")


    
def checkoutdetails(request):
    t = loader.get_template('checkoutdetails.html')
    order = Order.objects.get(pk=request.session.get("order_id", 0))
    msg = ''

    if request.POST:
        rp = request.POST.copy()
        if rp.get("editmyorder", None):
            return HttpResponseRedirect("cart.html")
        if rp.get("copydata", None):
            if rp.get("billfirstname", None):
                rp["shipfirstname"] = rp.get("billfirstname")
                rp["shiplastname"] = rp.get("billlastname")
                rp["shipcompany"] = rp.get("billcompany")
                rp["shipaddress"] = rp.get("billaddress")
                rp["shipaddress2"] = rp.get("billaddress2")
                rp["shipaddress3"] = rp.get("billaddress3")
                rp["shipsuburb"] = rp.get("billsuburb")
                rp["shipstate"] = rp.get("billstate")
                rp["shippostcode"] = rp.get("billpostcode")
                rp["shipcountry"] = rp.get("billcountry")
                rp["shipphone"] = rp.get("billphone")
            else:
                rp["billfirstname"] = rp.get("shipfirstname")
                rp["billlastname"] = rp.get("shiplastname")
                rp["billcompany"] = rp.get("shipcompany")
                rp["billaddress"] = rp.get("shipaddress")
                rp["billaddress2"] = rp.get("shipaddress2")
                rp["billaddress3"] = rp.get("shipaddress3")
                rp["billsuburb"] = rp.get("shipsuburb")
                rp["billstate"] = rp.get("shipstate")
                rp["billpostcode"] = request.session["shippingpostcode"]
                rp["billcountry"] = Country.objects.get(country__iexact=request.session["shippingcountry"]).id 
                rp["billphone"] = rp.get("shipphone")
        
        rp["shippostcode"] = request.session["shippingpostcode"]
        rp["shipcountry"] = Country.objects.get(country__iexact=request.session["shippingcountry"]).id 
        shipCountry = Country.objects.get(pk=int(rp.get("shipcountry", 0)))
        form = CustomerDetailsForm(rp)
        '''if (rp.get("shipcountry") and int(rp.get("shipcountry", 0))):
            shipCountry = Country.objects.get(pk=int(rp.get("shipcountry", 0)))
            request.session["shippingcountry"] = shipCountry.country
        if rp.get("shippostcode", ""):
            request.session["shippingpostcode"] = rp.get("shippostcode", "")'''
        if form.is_valid(): # All validation rules pass
            email = rp.get("billemail", "").strip().lower()
            username = rp.get("billemail", "").strip().lower()
            username = username.replace("@", "_")
            username = username.replace(".", "_")
            u, created = User.objects.get_or_create(username="retail_"+username)
            u.is_active = False
            if created:
                u.set_unusable_password()
            u.email = email
            u.first_name = rp.get("billfirstname", "?")
            u.last_name = rp.get("billlastname", "?")
            u.save()
            if u:
                order.user = u
                order.save()
            try:
                profile = u.get_profile()
            except:
                profile = Profile()
                u.profile_set.add(profile)
                Log(u, "Creating New Profile")
            profile.phone = rp.get("billphone", "")
            profile.company = rp.get("billcompany", "")
            profile.subscribe = bool(int(rp.get("subscribe", "")))
            try:
                billing = profile.billing_set.all()[0]
            except:
                billing = Billing()
                billing.profile = profile
            billing.first_name = rp.get("billfirstname", "")
            billing.last_name = rp.get("billlastname", "")
            billing.company = rp.get("billcompany", "")
            billing.address = rp.get("billaddress", "")
            billing.address2 = rp.get("billaddress2", "")
            billing.address3 = rp.get("billaddress3", "")
            billing.suburb = rp.get("billsuburb", "")
            billing.state = rp.get("billstate", "")
            billing.postcode = rp.get("billpostcode", "")
            billing.country = Country.objects.get(pk=int(rp.get("billcountry", 0)))
            billing.phone = rp.get("billphone", "")
            billing.save()
            Log(u, "Saved Billing Information", billing)
            try:
                shipping = profile.shipping_set.all()[0]
            except:
                shipping = Shipping()
                shipping.profile = profile
            shipping.first_name = rp.get("shipfirstname", "")
            shipping.last_name = rp.get("shiplastname", "")
            shipping.company = rp.get("shipcompany", "")
            shipping.address = rp.get("shipaddress", "")
            shipping.address2 = rp.get("shipaddress2", "")
            shipping.address3 = rp.get("shipaddress3", "")
            shipping.suburb = rp.get("shipsuburb", "")
            shipping.state = rp.get("shipstate", "")
            shipping.postcode = rp.get("shippostcode", "")
            shipping.country = shipCountry
            shipping.phone = rp.get("shipphone", "")
            shipping.save()
            
            Log(u, "Saved Shipping Information", shipping)
            request.session["contactdata"] = rp
            return HttpResponseRedirect("/shop/confirmdetails.html")
            return HttpResponseRedirect("/shop/payment.html")
    else:
        if request.session.has_key("contactdata"):
            request.session["contactdata"]["shippostcode"] = request.session["shippingpostcode"]
            request.session["contactdata"]["shipcountry"] = Country.objects.get(country__iexact=request.session["shippingcountry"]).id 
            form = CustomerDetailsForm(request.session["contactdata"])
        else:
            rp = {}
            if request.session.get("shippingcountry"):
                sc = Country.objects.filter(country=request.session.get("shippingcountry"))
                rp['shipcountry'] = sc[0].id if sc else None
                rp['billcountry'] = sc[0].id if sc else None
                rp['shippostcode'] = request.session["shippingpostcode"]
            form = CustomerDetailsForm(initial=rp)
    country = request.session.get("shippingcountry", None)
    postcode = request.session.get("shippingpostcode", None)
    order = Order.objects.get(pk=request.session.get("order_id", 0), status=OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS))
    weight = order.getTotalWeight()
    try:
        if country.strip().lower() == "australia":
            price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
        else:
            price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())
        if not price:
            price = "?"
        price = 0.00 if price =='free' else price    
    except Exception, e:
        price = "?"
    if country.strip().lower() == "australia":
        tax = float(order.getTotalGST())
    else:
        tax = 0.00
    totalprice = float(order.getTotalTaxFreePrice())+tax+price
    d = {
        "order": order,
        "shippingcost": common.formatCurrency(guessShippingCost(request)),
        "countries": Country.objects.filter(shipto=True).order_by("country"),
        "totalcost": common.formatCurrency(totalprice),
        "taxcost": common.formatCurrency(tax),
        'form': form,
        'msg':msg
        }
    if request.session.get("shippingcountry"):
        d["shippingcountry"] = request.session.get("shippingcountry")
    if request.session.get("shippingpostcode"):
        d["shippingpostcode"] = request.session.get("shippingpostcode")
    c = RequestContext(request,common.commonDict(d, request))
    return HttpResponse(t.render(c))
def confirmdetails(request):
    rp = request.POST.copy()
    order = Order.objects.get(pk=request.session.get("order_id", 0))
    u = order.user
    if rp.get("editmydetails", None) and request.user and request.user.is_active:
        return HttpResponseRedirect("/wholesale/shipping.html")
    if rp.get("editmydetails", None):
        return HttpResponseRedirect("details.html")
    if rp.get("editmyorder", None):
        return HttpResponseRedirect("cart.html")
    if rp.get("submitthisorder", None):
        order.status = OrderStatus.objects.get(status__iexact='pending')
        order.save()
        profile = u.get_profile()
        shipping = profile.shipping_set.all()
        if shipping:
            shipping = shipping[0]
        billing = profile.billing_set.all()
        if billing:
            billing = billing[0]
        
        payment = False
        t = loader.get_template('orderconfirmationemail.html')
        d = {"profile":profile, "shipping":shipping, "billing":billing,'payment':payment}
        c = RequestContext(request,common.commonDict(d, request))
        msg = t.render(c)
        email = EmailMultiAlternatives('EASTBOURNEART Order Received - Order '+ order.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', ['orders@eastbourneart.com.au',order.user.email])
        email.attach_alternative(msg, "text/html")
        email.send()
        '''---------------------------------------inventory----------------------------------------------'''
        pos = order.productorder_set.all()
        for x in pos:
            if x.product.inventory:
                x.product.inventory -= x.quantity
                x.product.save()
                if x.product.inventory <= x.product.maximum_quantity_wholesale:
                    t = loader.get_template('productinshort.html')
                    c = RequestContext(request,{'product':x.product})
                    msg = t.render(c)
                    send_mail('EASTBOURNEART Product In Short - Product '+ x.product.title, msg, 'no-reply@eastbourneart.com.au', ['eastbourneart@bigpond.com','orders@eastbourneart.com.au'], fail_silently=False)
        '''----------------------------------------------------------------------------------------------'''
        
        
        #send_mail('EASTBOURNEART Order Received - Order '+ order.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', [order.user.email], fail_silently=False)
        '''coupon =  request.session.get('coupon')
        coupons = Coupon.objects.all()
        for x in coupons:
            r = x if x.checkCode(coupon) else None'''
        #if r:
            #r.addUsed(coupon)
            
        request.session["order_id"] = None
        request.session['coupon'] = ''
        return HttpResponseRedirect("success%s.html" % order.id)
    if request.POST:
        return HttpResponseRedirect("payment.html")
    if request.user.is_active:
        t = loader.get_template('wholesalecheckoutconfirmdetails.html')
    else:
        t = loader.get_template('checkoutconfirmdetails.html')
    profile = u.get_profile()
    country = request.session.get("shippingcountry", None)
    postcode = request.session.get("shippingpostcode", None)
    order = Order.objects.get(pk=request.session.get("order_id", 0), status=OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS))
    weight = order.getTotalWeight()
    if not request.user.is_active:
        try:
            if country.strip().lower() == "australia":
                price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
            else:
                price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())
            if not price:
                price = "?"
            price = 0.00 if price == 'free' else price
        except Exception, e:
            price = "?"
    else:
        price = 0.0
    if country.strip().lower() == "australia":
        tax = float(order.getTotalGST())
    else:
        tax = 0.00
    totalprice = float(order.getTotalTaxFreePrice())+tax+price
    d = {
        "order": order,
        "shippingcost": common.formatCurrency(guessShippingCost(request)),
        "countries": Country.objects.filter(shipto=True).order_by("country"),
        "totalcost": common.formatCurrency(totalprice),
        "taxcost": common.formatCurrency(tax),
        'profile': profile,
        'usr': u,
        }
    try:
        d["billing"] = profile.billing_set.filter()[0]
    except:
        d["billing"] = Billing()
        d["billing"].profile = profile
    try:
        d["shipping"] = profile.shipping_set.filter()[0]
    except:
        d["shipping"] = Shipping()
        d["shipping"].profile = profile
    #return HttpResponse(str(d["shipping"]))
    c = RequestContext(request,common.commonDict(d, request))
    return HttpResponse(t.render(c))
def payment(request):
    # TODO logging needs to be added into here
    msg = ''
    form = ''
    t = loader.get_template('payment.html')
    message = ''
    if request.session.get("order_id", None):
        order = Order.objects.get(pk=request.session.get("order_id", 0))
    else:
        raise ValueError("Order not found")
  
    '''-------------------------------paypal-------------------------------------------------'''
    if request.POST.get("paypalcheckout.x", None):
        if float(order.getShippingCharged()) != 0:
            msgg = common.getResponse(order)
            
            if msgg['ACK'] == 'Success':
                        
                return HttpResponseRedirect("https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=%s&useraction=commit" % msgg['TOKEN'])
            else:
                msg = msgg
                '''----------------------------------------------------------------------------------------'''
    
    elif request.POST:
        rp = request.POST.copy()
        if rp.get("editmyorder"):
            return HttpResponseRedirect("cart.html")
        form = CreditCardForm(rp)
        if form.is_valid():
            profile = order.user.get_profile()
            shipping = profile.shipping_set.all()
            billing = profile.billing_set.all()
            customer = Customer()
            names = form.cleaned_data.get("name")
            firstname = names[0]
            lastname = names[1]
            customer.first_name = firstname
            customer.last_name = lastname
            customer.email = billing[0].email
            customer.address = billing[0].address
            customer.postcode = billing[0].postcode
            customer.invoice_description = "Order from eastbourneart"
            customer.invoice_reference = order.getOrderNumber()
            customer.country = billing[0].country
            
            #op = CreditPayment()
            credit_card = CreditCard()
            #op.type = form.cleaned_data.get("type")
            credit_card.number = form.cleaned_data.get("number")
            credit_card.expiry_month = form.cleaned_data.get("expiryMonth")
            credit_card.expiry_year = form.cleaned_data.get("expiryYear")
            
            credit_card.holder_name = '%s %s' % (firstname, lastname,)
            credit_card.verification_number = form.cleaned_data.get("CVV")
            credit_card.ip_address = request.META["REMOTE_ADDR"]
            
            amount = float(order.total_charged)
            
            if customer.is_valid() and credit_card.is_valid():
                
                                                #17019375 
                eway_client =  EwayPaymentClient('17019375',config.REAL_TIME_CVN,True)
                response = eway_client.authorize(Decimal(str(amount)), credit_card=credit_card, customer=customer)
                if response.status.lower() =='true':
                    order.status = OrderStatus.objects.get(status__iexact=settings.TXT_SHOP_ORDER_STATUS_ORDERED)
                    order.save()
                    payment = True
                    t = loader.get_template('orderconfirmationemail.html')
                    d = {"profile":profile, "shipping":shipping[0], "billing":billing[0],'payment':payment}
                    c = RequestContext(request,common.commonDict(d, request))
                    msg = t.render(c)
                    email = EmailMultiAlternatives('EASTBOURNEART Order Received - Order '+ order.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', ['orders@eastbourneart.com.au', order.user.email])
                    email.attach_alternative(msg, "text/html")
                    email.send()
                    
                    '''---------------------------------------inventory----------------------------------------------'''
                    pos = order.productorder_set.all()
                    for x in pos:
                        if x.product.inventory:
                            x.product.inventory -= x.quantity
                            x.product.save()
                            if x.product.inventory <= x.product.maximum_quantity_wholesale:
                                t = loader.get_template('productinshort.html')
                                c = RequestContext(request,{'product':x.product})
                                msg = t.render(c)
                                send_mail('EASTBOURNEART Product In Short - Product '+ x.product.title, msg, 'no-reply@eastbourneart.com.au', ['eastbourneart@bigpond.com','orders@eastbourneart.com.au'], fail_silently=False)
                    '''----------------------------------------------------------------------------------------------'''
                    
                    '''coupon =  request.session.get('coupon')
                    coupons = Coupon.objects.all()
                    for x in coupons:
                        r = x if x.checkCode(coupon) else None'''
                    #if r:
                        #r.addUsed(coupon)
               # send_mail('EASTBOURNEART Order Received - Order '+ order.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', [order.user.email], fail_silently=False)
                    request.session["order_id"] = None
                    request.session['coupon'] = ''
                    return HttpResponseRedirect("success%s.html" % order.id)
                else:
                    message = response.error
                    
            else:
                return HttpResponse("ERROR: %s" % "Please supply all required infomation")
    else:
        form = CreditCardForm()
    country = request.session.get("shippingcountry", None)
    postcode = request.session.get("shippingpostcode", None)
    weight = order.getTotalWeight()
    try:
        if country.strip().lower() == "australia":
            price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
        else:
            price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())
        if not price:
            price = "?"
        price = 0.00 if price =='free' else price
    except Exception, e:
        price = "?"
    if country.strip().lower() == "australia":
        tax = float(order.getTotalGST())
    else:
        tax = 0.00
    totalprice = float(order.getTotalTaxFreePrice())+tax+price
    d = {
        'form': form,
        "hash": generateAmountHash(common.formatCurrency(totalprice)),
        "shippingcost": common.formatCurrency(price),
        "totalcost": common.formatCurrency(totalprice),
        "taxcost": common.formatCurrency(tax),
        "message":message,
        'msg':msg,
    }
    c = RequestContext(request,common.commonDict(d, request))
    return HttpResponse(t.render(c))



def success(request, orderid):
    msgg=''
    if request.GET:

        order = Order.objects.filter(id = orderid)
        if order:
            order = order[0]
            profile = order.user.get_profile()
            shipping = profile.shipping_set.all()
            billing = profile.billing_set.all()
            token = request.GET.get('token')
            payerid = request.GET.get('PayerID')
            response = common.getResponse(order, action='do', token=token, payerid=payerid)
            msgg = response
            if response['ACK'] == 'Success':
                
                
                order.status = OrderStatus.objects.get(status__iexact=settings.TXT_SHOP_ORDER_STATUS_ORDERED)
                order.save()
                payment = True
                t = loader.get_template('orderconfirmationemail.html')
                d = {"profile":profile, "shipping":shipping[0], "billing":billing[0],'payment':payment}
                c = RequestContext(request,common.commonDict(d, request))
                msg = t.render(c)
                email = EmailMultiAlternatives('EASTBOURNEART Order Received - Order '+ order.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', ['orders@eastbourneart.com.au', order.user.email])
                email.attach_alternative(msg, "text/html")
               # email.send()
                    
                '''---------------------------------------inventory----------------------------------------------'''
                pos = order.productorder_set.all()
                for x in pos:
                    if x.product.inventory:
                        x.product.inventory -= x.quantity
                        x.product.save()
                        if x.product.inventory <= x.product.maximum_quantity_wholesale:
                            t = loader.get_template('productinshort.html')
                            c = RequestContext(request,{'product':x.product})
                            msg = t.render(c)
                            send_mail('EASTBOURNEART Product In Short - Product '+ x.product.title, msg, 'no-reply@eastbourneart.com.au', ['eastbourneart@bigpond.com','orders@eastbourneart.com.au'], fail_silently=False)
                    '''----------------------------------------------------------------------------------------------'''
                    
                '''coupon =  request.session.get('coupon')
                coupons = Coupon.objects.all()
                for x in coupons:
                    r = x if x.checkCode(coupon) else None'''
                #if r:
                    #r.addUsed(coupon)
               # send_mail('EASTBOURNEART Order Received - Order '+ order.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', [order.user.email], fail_silently=False)
                request.session["order_id"] = None
                request.session['coupon'] = ''
                t = loader.get_template('success.html')
            else:
                t = loader.get_template('confirm.html')
                msgg = 'Sorry, we cannot checkout your order with paypal, please pay by another method.'
    else:
         
        t = loader.get_template('success.html')
    c = RequestContext(request,common.commonDict({
        'orderid': orderid.zfill(4),
        'msg':msgg
    }, request))
    return HttpResponse(t.render(c))
def cart(request):
    msg = ''
    t = loader.get_template('cart.html')
    if request.session.get("order_id", None):
        order = Order.objects.get(pk=request.session.get("order_id", 0))
    else:
        order = None
    if order:
        country = request.session.get("shippingcountry", None)
        postcode = request.session.get("shippingpostcode", None)
        print country, postcode
        weight = order.getTotalWeight()
        if not request.user.is_active:
            try:
                if country.strip().lower() == "australia":
                    price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
                else:
                    price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())#calculateshipping(country, postcode, weight)
                realprice = price
                if not price:
                    price = "?"
                    realprice = 0.0
                realprice = 0.0 if realprice == 'free' else realprice
                price = 0.00 if price == 'free' else price
            except Exception, e:
                print e
                price = "?"
                realprice = 0.0
        else:
            realprice = 0.0
        if country and country.strip().lower() == "australia":
            tax = float(order.getTotalGST())
        else:
            tax = 0.00
        totalprice = float(order.getTotalTaxFreePrice())+tax+realprice
        if request.POST:
            if request.POST.get("changequantity", None):
                for x in request.POST.get("products", "").strip().split(" "):
                    x = int(x)
                    try:
                        op = order.productorder_set.get(pk=x)
                    except:
                        op = None
                    if op:
                        try:
                            quant = int(request.POST.get("quantity"+str(x), 1))
                            if quant > 0:
                                if quant < op.product.minimum_quantity:
                                    quant = op.product.minimum_quantity
                                op.quantity = quant
                                op.save()
                            else:
                                op.delete()
                            order = Order.objects.get(pk=request.session.get("order_id", 0), status=OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS))
                            if country.strip().lower() == "australia":
                                price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
                            else:
                                price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())#calculateshipping(country, postcode, weight)
                            price = 0.00 if price =='free' else price
                            order.shipping_charged = price
                            order.save()
                        except:
                            pass
                return HttpResponseRedirect("/shop/cart.html")
            elif request.POST.get("continueshopping", None):
                return HttpResponseRedirect(request.session.get("lastpage", "/"))
            elif request.POST.get("completemyorder", None):
                print request.user.is_active
                order.tax_charged = tax
                order.shipping_charged = realprice
                order.total_charged = totalprice
                order.save()
                if request.user.is_active:
                    #order.status = OrderStatus.objects.get(status__iexact="Ordered")
                    #request.session["order_id"] = None
                    return HttpResponseRedirect("confirmdetails.html")
                    #return HttpResponseRedirect("success%s.html" % order.id)
                    #raise ValueError("TODO workout what happened here")
                else:
                    return HttpResponseRedirect("details.html")
            
        d = {
            "order": order,
            "countries": Country.objects.filter(shipto=True).order_by("country"),
            "shippingcost": common.formatCurrency(guessShippingCost(request)),
            "totalcost": common.formatCurrency(totalprice),
            "taxcost": common.formatCurrency(tax),
            'msg':msg,
            }
        if request.session.get("shippingcountry"):
            d["shippingcountry"] = request.session.get("shippingcountry")

        if request.session.get("shippingpostcode"):
            d["shippingpostcode"] = request.session.get("shippingpostcode")
    else:
        d = {}
    c = RequestContext(request,common.commonDict(d, request))
    return HttpResponse(t.render(c))
def cartsummary(request):
    if request.session.get("order_id", None):
        order = Order.objects.get(pk=request.session.get("order_id", 0))
        return HttpResponse(simplejson.dumps({"items": order.getTotalItems(), "price": eastbourne.common.formatCurrency(float(order.getTotalTaxFreePrice()))}))
    else:
        return HttpResponse(simplejson.dumps({"items": "0", "price": "0.00"}))

def calculateshippingjson(request):
    rp = request.POST
    if rp.get("postcode"):
        request.session["shippingcountry"] = rp.get("country")
        request.session["shippingpostcode"] = rp.get("postcode")
    else:
        return HttpResponse(str({"error": "Post code is required"}))
    country = request.session.get("shippingcountry", None)
    postcode = request.session.get("shippingpostcode", None)
    weight = int(rp.get("weight", 0))
    price = 0
    order = Order.objects.get(pk=request.session.get("order_id", 0), status=OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS))
    try:
        if country.strip().lower() == "australia":
            price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
        else:
            price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())#calculateshipping(country, postcode, weight)
        if not price:
            return HttpResponse(str({"error": settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE}))
        price = 0.00 if price == 'free' else price
    except Exception, e:
        return HttpResponse(str({"error": str(e)}))
   
    order.shipping_charged = price
    
    if country.strip().lower() == "australia":
        tax = float(order.getTotalGST())
    else:
        tax = 0.00
    totalprice = float(order.getTotalTaxFreePrice())+tax+price
    order.total_charged = totalprice
    order.save()
    return HttpResponse(simplejson.dumps({"shippingprice": common.formatCurrency(price), "tax": common.formatCurrency(tax), "totalprice": common.formatCurrency(totalprice)}))
def guessShippingCost(request):
    country = request.session.get("shippingcountry", None)
    postcode = request.session.get("shippingpostcode", None)
    order = Order.objects.get(pk=request.session.get("order_id", 0), status=OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS))
    weight = order.getTotalWeight()
    if not request.user.is_active:
        try:
            if country.strip().lower() == "australia":
                price = postAustralia(getBoxes(order),getBoxWeight(order),postcode,order.getTotal())
            else:
                price = postInternational(getBoxes(order),getBoxWeight(order),postcode,country,order.getTotal())#calculateshipping(country, postcode, weight)
            price = 0.00 if price == 'free' else price
        except:
            price = "?"
    else:
        price = 0.0
    return price
def addtocart(request):
    print request.user
    rp = request.GET
    product = Product.objects.get(pk=rp["id"])
    try:
        order = Order.objects.get(pk=request.session.get("order_id", 0), status=OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS))
    except:
        order = Order()
        order.status = OrderStatus.objects.get(status=settings.TXT_SHOP_ORDER_STATUS_IN_PROGRESS)
        order.save()
    if not order.user and request.user and type(request.user) != AnonymousUser:
        order.user = request.user
        order.save()
    request.session["order_id"] = order.id
    coupon = request.session.get('coupon', '')
    style = rp.get("style", None)
    if style:
        style = Style.objects.get(code=style)
    size = rp.get("size", "")
    if size:
        size = Size.objects.get(code=size)
    try:
        op = order.productorder_set.filter(product__pk=product.id)
        if style:
            op = op.filter(style__code=style.code)
        if size:
            op = op.filter(size__code=size.code)
        productorder = op[0]
        productorder.quantity += int(rp.get("quantity", 0))
        productorder.price = product.getTaxFreePrice(size,request.user.is_active,coupon)
        if product.getNormalPrice(request.user.is_active) != productorder.price:
            cp = Coupon.objects.filter(codes=coupon)
            cp = cp[0] if cp else None
            dcp = cp.discountprice_set.filter(product__title=product.title) if cp else None
            dcp = dcp[0] if dcp else None
            productorder.coupon = coupon if dcp and dcp.getPrice(request.user.is_active) == productorder.price else None
        productorder.save()
    except Exception, e:
        productorder = ProductOrder()
        if style:
            productorder.style = style
        if size:
            productorder.size = size
        productorder.product = product
        productorder.quantity = rp.get("quantity", 0)
        productorder.price = product.getTaxFreePrice(size,request.user.is_active,coupon)
        if product.getNormalPrice(request.user.is_active) != productorder.price:
            cp = Coupon.objects.filter(codes=coupon)
            cp = cp[0] if cp else None
            dcp = cp.discountprice_set.filter(product__title=product.title) if cp else None
            dcp = dcp[0] if dcp else None
            productorder.coupon = coupon if dcp and dcp.getPrice(request.user.is_active) == productorder.price else None
        productorder.order = order
        productorder.save()
    return HttpResponse(simplejson.dumps({"items": order.getTotalItems(), "price": eastbourne.common.formatCurrency(float(order.getTotalTaxFreePrice()) )}))

def getprice(request):
    rp = request.POST
    product = Product.objects.get(pk=rp.get("id",""))
    size = Size.objects.get(code=rp.get('size',""))
    number = int(rp.get('number',"1"))
    coupon = rp.get('coupon','')
    if number ==1 :
    #sale = rp.get('sale',False)
        price = product.getTaxFreePrice(size,False,coupon)
    else:
        price = product.getTaxFreePrice(size,True,coupon)
    return HttpResponse(str({"price": price}))