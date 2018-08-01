'''
@author: chaol
'''

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import datetime, time
from models import *
from django.db import connection

from django.core.cache import cache
from django.core.paginator import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout
from eastbourne.userprofile.models import *
from django.conf import settings

from ShopLogging import Log
import string
from eastbourne import common
from forms import *
import random

from django.core.mail import send_mail

from django.db.models.signals import pre_save
from django.db.models.signals import post_save

def userCreated(sender, **kwargs):
    usr = kwargs["instance"]
    if kwargs["created"]:
        p = Profile(user=usr)
        p.save()
post_save.connect(userCreated, sender=User)



def home(request):
    return HttpResponse("Wholesalers Home")
def registered(request):
    t = loader.get_template('wholesale_registered.html')
    c = RequestContext(request,common.commonDict({}, request))
    return HttpResponse(t.render(c))
def forgotpassword(request):
    t = loader.get_template('wholesale_forgotpassword.html')
    data = {}
    if request.POST:
        rp = request.POST.copy()
        resetform = WholesaleForgotPasswordForm(rp)
        if resetform.is_valid():
            try:
                User.objects.get(email=resetform.cleaned_data["email"])
                exists = True
            except:
                exists = False
            if exists:
                characters = string.ascii_lowercase + string.digits
                characters = characters.replace("0", "").replace("1", "").replace("l", "")
                characters = [x for x in characters]
                random.shuffle(characters)
                user = User.objects.get(email=resetform.cleaned_data['email'], is_active=True)
                newpass = "".join(characters[:8])
                user.set_password(newpass)
                user.save()
                data["newpassword"] = newpass
                msg = """Hi,
    Your request to reset your password on EastbourneArt has been completed.
    
    Your new password is: %s
    
    Please login at https://www.eastbourneart.com.au/wholesale/
    
    You can change this password to one which is more memorable by logging on at https://www.eastbournart.com.au/wholesale/ and updating your profile.
    
    ---------
    
    The IP address from which the password request was received was %s""" % (newpass, request.META.get('REMOTE_ADDR'))
                send_mail("EastbourneArt Password Reset Request", msg, 'no-reply@eastbourneart.com.au', [user.email], fail_silently=False)
                data["message"] = "We've sent a new password to your email address."
            else:
                data["message"] = "We were unable to find your email address."
        else:
            pass
    else:
        resetform = WholesaleForgotPasswordForm()
    data["form"] = resetform
    c = RequestContext(request,common.commonDict(data, request))
    return HttpResponse(t.render(c))
def order(request, id):
    Order.objects.get(pk=int(id), user=request.user)
    t = loader.get_template('wholesale_order.html')
    c = RequestContext(request,common.commonDict({
        'order': Order.objects.get(pk=int(id), user=request.user),
    }, request))
    return HttpResponse(t.render(c))
def orders(request):
    t = loader.get_template('wholesale_orders.html')
    c = RequestContext(request,common.commonDict({
        'orders': Order.objects.filter(user=request.user).order_by("-started"),
    }, request))
    return HttpResponse(t.render(c))
def profile(request):
    u = request.user
    t = loader.get_template('wholesale_profile.html')
    if request.POST and request.POST.get("contactupdate"):
        rp = request.POST.copy()
        contactform = WholesaleProfilePrimaryContactForm(rp)
        if contactform.is_valid():
            profile = u.get_profile()
            profile.subscribe = int(contactform.cleaned_data["subscribe"])
            profile.phone = contactform.cleaned_data["phone"]
            profile.phone2 = contactform.cleaned_data["phone2"]
            profile.fax = contactform.cleaned_data["fax"]
            profile.company = contactform.cleaned_data["company"]
            profile.tradingas = contactform.cleaned_data["tradingas"]
            profile.abn = contactform.cleaned_data["abn"]
            profile.save()
            u.first_name = contactform.cleaned_data["firstname"]
            u.last_name = contactform.cleaned_data["lastname"]
            u.save()
    else:
        u = request.user
        rp = {
              "firstname": u.first_name,
              "lastname": u.last_name,
              "company": u.get_profile().company,
              "tradingas": u.get_profile().tradingas,
              "abn": u.get_profile().abn,
              "phone": u.get_profile().phone,
              "phone2": u.get_profile().phone2,
              "fax": u.get_profile().fax,
              "subscribe": int(u.get_profile().subscribe),
              }
        contactform = WholesaleProfilePrimaryContactForm(rp)
    if request.POST and request.POST.get("emailupdate"):
        rp = request.POST.copy()
        emailform = WholesaleProfileEmailForm(rp)
        if emailform.is_valid():
            request.user.email = emailform.cleaned_data["email"]
            
            email = emailform.cleaned_data["email"].strip().lower()
            username = email
            username = username.replace("@", "_")
            username = username.replace(".", "_")
            
            request.user.username = username
            
            request.user.save()
    else:
        emailform = WholesaleProfileEmailForm()
    if request.POST and request.POST.get("passwordupdate"):
        rp = request.POST.copy()
        passwordform = WholesaleProfilePasswordForm(rp)
        if passwordform.is_valid():
            u.set_password(passwordform.cleaned_data["password"])
            u.save()
    else:
        passwordform = WholesaleProfilePasswordForm()
    c = RequestContext(request,common.commonDict({
        "contactform": contactform,
        "emailform": emailform,
        "passwordform": passwordform,
        "openpath": ["profile"],
    }, request))
    return HttpResponse(t.render(c))
def shipping(request):
    u = request.user
    t = loader.get_template('wholesale_shipping.html')
    updated = False
    profile = u.get_profile()
    test = ""
    
    if request.POST and request.POST.get("update"):
        rp = request.POST.copy()
        rp.setdefault("agree", True)
        test = rp.lists()
        if rp.get("copydata"):
            rp["billfirstname"] = rp["shipfirstname"]
            rp["billlastname"]= rp["shiplastname"] 
            rp["billcompany"] = rp["shipcompany"]
            rp["billaddress"] = rp["shipaddress"] 
            rp["billaddress2"] = rp["shipaddress2"] 
            rp["billaddress3"] = rp["shipaddress3"] 
            rp["billsuburb"] = rp["shipsuburb"] 
            rp["billstate"] = rp["shipstate"] 
            rp["billpostcode"] = rp["shippostcode"] 
            rp["billcountry"] = rp["shipcountry"] 
            rp["billphone"] = rp["shipphone"] 
            rp["billemail"] = u.email
        addressform = CustomerWDetailsForm(rp)
        if addressform.is_valid():
            s = profile.shipping_set.all()
            if s:
                shipping = s[0]
            else:
                shipping = Shipping()
                shipping.profile = profile
            shipping.first_name = addressform.cleaned_data["shipfirstname"]
            shipping.last_name = addressform.cleaned_data["shiplastname"]
            shipping.company = addressform.cleaned_data["shipcompany"]
            shipping.address = addressform.cleaned_data["shipaddress"]
            shipping.address2 = addressform.cleaned_data["shipaddress2"]
            shipping.address3 = addressform.cleaned_data["shipaddress3"]
            shipping.suburb = addressform.cleaned_data["shipsuburb"]
            shipping.state = addressform.cleaned_data["shipstate"]
            shipping.postcode = addressform.cleaned_data["shippostcode"]
            shipping.country = addressform.cleaned_data["shipcountry"]
            shipping.phone = addressform.cleaned_data["shipphone"]
            request.session["shippingcountry"] = shipping.country.country
            request.session["shippingpostcode"] = shipping.postcode
            shipping.save()
            b = profile.billing_set.all()
            if len(list(b)):
                billing = b[0]
            else:
                billing = Billing()
                billing.profile = profile
            billing.first_name = addressform.cleaned_data["billfirstname"]
            billing.last_name = addressform.cleaned_data["billlastname"]
            billing.company = addressform.cleaned_data["billcompany"]
            billing.address = addressform.cleaned_data["billaddress"]
            billing.address2 = addressform.cleaned_data["billaddress2"]
            billing.address3 = addressform.cleaned_data["billaddress3"]
            billing.suburb = addressform.cleaned_data["billsuburb"]
            billing.state = addressform.cleaned_data["billstate"]
            billing.postcode = addressform.cleaned_data["billpostcode"]
            billing.country = addressform.cleaned_data["billcountry"]
            billing.phone = addressform.cleaned_data["billphone"]
            billing.email = addressform.cleaned_data["billemail"]
            billing.save()
            updated = True
            profile.subscribe = bool(int(rp.get("subscribe", 0)))
            profile.save()
    else:
        try:
            shipping = u.get_profile().shipping_set.all()[0]
        except:
            shipping = Shipping()
        try:
            billing = u.get_profile().billing_set.all()[0]
        except:
            billing = Billing()
        rp = {
              "billfirstname": billing.first_name,
              "billlastname": billing.last_name,
              "billcompany": billing.company,
              "billaddress": billing.address,
              "billaddress2": billing.address2,
              "billaddress3": billing.address3,
              "billsuburb": billing.suburb,
              "billstate": billing.state,
              "billpostcode": billing.postcode,
              "billphone": billing.phone,
              "billemail": billing.email,
              
              "shipfirstname": shipping.first_name,
              "shiplastname": shipping.last_name,
              "shipcompany": shipping.company,
              "shipaddress": shipping.address,
              "shipaddress2": shipping.address2,
              "shipaddress3": shipping.address3,
              "shipsuburb": shipping.suburb,
              "shipstate": shipping.state,
              "shippostcode": shipping.postcode,
              "shipphone": shipping.phone,
              "subscribe": int(profile.subscribe),
              }
        try:
            rp["billcountry"] = billing.country.id
        except Exception, e:
           # return HttpResponse(str(e))
            pass
        try:
            rp["shipcountry"] = shipping.country.id
        except:
            pass
        addressform = CustomerWDetailsForm(initial=rp)
    
    c = RequestContext(request,common.commonDict({
        "test" : test,
        "addressform": addressform,
        "openpath": ["profile"],
        "updated": updated,
    }, request))
    return HttpResponse(t.render(c))
def logout(request):
    if not request.GET.get("success"):
        _logout(request)
        return HttpResponseRedirect("logout.html?success=1")
    else:
        t = loader.get_template('loggedout.html')
        c = RequestContext(request,common.commonDict({}, request))
        return HttpResponse(t.render(c))
def login(request):
    if request.user.is_active:
        return HttpResponseRedirect("/")
    t = loader.get_template('wholesale_login.html')
    rp = request.POST.copy()
    if rp.get("register"):
        return HttpResponseRedirect("register.html")
    if rp:
        form = WholesaleLoginForm(rp)
        if form.is_valid():
            if request.session.has_key('order_id'):
                _logout(request)
            _login(request, form.user)
            profile = request.user.get_profile()

            request.session["shippingcountry"] = profile.shipping_set.get().country.country
            request.session["shippingpostcode"] = profile.shipping_set.get().postcode
            #print request.session.keys(), request.session["shippingcountry"]
            return HttpResponseRedirect("/")
    else:
        form = WholesaleLoginForm()
    c = RequestContext(request,common.commonDict({
        'form': form,
    }, request))
    return HttpResponse(t.render(c))
def register(request):
    t = loader.get_template('wholesale_register.html')
    rp = request.POST.copy()
    if rp:
        form = WholesaleForm(rp)
        if form.is_valid():
            try:
                
                email = form.cleaned_data["email"].strip().lower()
                if form.cleaned_data["subscribe"] == "1":
                    s, created = Subscription.objects.get_or_create(email=email, defaults={"is_wholesale": True, "ip": request.META["REMOTE_ADDR"]})
                username = email
                username = username.replace("@", "_")
                username = username.replace(".", "_")
                try:
                    u, created = User.objects.get_or_create(username=username, defaults={"email": email, "first_name": form.cleaned_data["firstname"], "last_name": form.cleaned_data["lastname"], "is_active": False})
                    u.set_password(form.cleaned_data["password"])
                    u.save()
                except Exception, e:
                    return HttpResponse("Error creating user: "+str(e))
                request.user = u
            except Exception, e:
                return HttpResponse("Error creating user profile: "+str(e))
            try:
                profile = u.get_profile()
            except Exception, e:
                return HttpResponse("Error fetching profile: "+str(e))
            try:
                profile.phone = form.cleaned_data["phone"]
                profile.phone2 = form.cleaned_data["phone2"]
                profile.fax = form.cleaned_data["fax"]
                profile.company = form.cleaned_data["company"]
                profile.tradingas = form.cleaned_data["tradingas"]
                profile.abn = form.cleaned_data["abn"]
                profile.wholesale = True
                profile.subscribe = False
                if form.cleaned_data["subscribe"] == "1":
                    profile.subscribe = True
                    
                profile.save()
            
                if not len(profile.shipping_set.all()):
                    shipping = Shipping()
                else:
                    shipping = profile.shipping_set.get()
                shipping.profile = profile
                shipping.first_name = form.cleaned_data["firstname"]
                shipping.last_name = form.cleaned_data["lastname"]
                shipping.company = form.cleaned_data["company"]
                shipping.address = form.cleaned_data["address"]
                shipping.address2 = form.cleaned_data["address2"]
                shipping.address3 = form.cleaned_data["address3"]
                shipping.suburb = form.cleaned_data["suburb"]
                shipping.state = form.cleaned_data["state"]
                shipping.postcode = form.cleaned_data["postcode"]
                shipping.country = form.cleaned_data["country"]
                shipping.phone = form.cleaned_data["phone"]
                shipping.save()
                if not len(profile.billing_set.all()):
                    billing = Billing()
                else:
                    billing = profile.billing_set.get()
                    
                billing.profile = profile
                billing.first_name = form.cleaned_data["firstname"]
                billing.last_name = form.cleaned_data["lastname"]
                billing.company = form.cleaned_data["company"]
                billing.address = form.cleaned_data["address"]
                billing.address2 = form.cleaned_data["address2"]
                billing.address3 = form.cleaned_data["address3"]
                billing.suburb = form.cleaned_data["suburb"]
                billing.state = form.cleaned_data["state"]
                billing.postcode = form.cleaned_data["postcode"]
                billing.country = form.cleaned_data["country"]
                billing.phone = form.cleaned_data["phone"]
                billing.save()
                #u.save()
            except Exception, e:
                return HttpResponse("Error saving extra profile information: "+str(e))
            return HttpResponseRedirect("registered.html")
    else:
        form = WholesaleForm()
    c = RequestContext(request,common.commonDict({
        'form': form,
    }, request))
    return HttpResponse(t.render(c))
