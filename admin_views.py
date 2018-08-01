'''
@author: chaol
'''

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import datetime, time
import csv
import csv2input
import os
import sys
from eastbourne.shop.models import *
from eastbourne.website.models import *
from django.contrib.auth.models import User
from django.db import connection
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout
from eastbourne import helpers
from django.db.models import *
def order(request, id):
    t = loader.get_template('admin/shop/order/full_order.html')
    order = Order.objects.get(pk=id)
    profile = None
    if order.user:
        try:
            profile = order.user.get_profile()
        except: 
            pass
    #return HttpResponse(str(dir(profile)))
    #po = order.productorder_set.all()
    c = RequestContext(request,{"order": order, "title": "Order Details #%s" % order.getOrderNumber(), "app_label": "shop", "profile": profile})
    return HttpResponse(t.render(c))

def invoice(request,id):
    t = loader.get_template('admin/shop/order/invoice.html')
    order = Order.objects.get(pk=id)
    profile = None
    if order.user:
        try:
            profile = order.user.get_profile()
        except: 
            pass
    #return HttpResponse(str(dir(profile)))
    #po = order.productorder_set.all()
    c = RequestContext(request,{"order": order, "title": "Invoice Number #%s" % str(order.id).zfill(8),"profile": profile})
    return HttpResponse(t.render(c))

def order_history(request, id):
    t = loader.get_template('admin/shop/order/order_history.html')
    user = User.objects.get(pk=id)
    profile = user.get_profile()
    orders = Order.objects.filter(user=user)
    c = RequestContext(request,{"orders": orders, "title": "Order History for %s" % user.email, "app_label": "shop", "profile": profile, "usr": user})
    return HttpResponse(t.render(c))

def productorder(request):
    t = loader.get_template('admin/shop/productorder/good_view.html')
    order =  ProductOrder.objects.filter(order__status__status="Ordered").order_by("product__category_now")
    products = order.values('product').distinct().annotate(Sum('quantity'))
    
    productorder = []
    for x in products:
        p = Product.objects.get(pk=x['product'])
        productorder.append((p, x['quantity__sum']))
        
    c = RequestContext(request,{'productorder':productorder})
    return HttpResponse(t.render(c))

def product_order(request, id):
    t = loader.get_template('admin/shop/productorder/product_order.html')
    order = ProductOrder.objects.filter(product__pk=id).filter(order__status__status="Ordered")
    c = RequestContext(request,{'order':order})
    return HttpResponse(t.render(c))

def myob(request):
    temp = []
    t= loader.get_template("admin/shop/order/myob.html")
    orders = Order.objects.filter(status__status__in=["Ordered","Shipped"])
    #spamWriter = csv.writer(open('/home/chaol/workspace/eastbourneart/media/myob/myob.txt', 'w'), delimiter=',')
    spamWriter = csv.writer(open('/var/www/vhosts/eastbourneart.com.au/httpdocs/media/myob/myob.txt', 'w'), delimiter=',')
    
    #spamWriter1 = csv.writer(open('/home/chaol/workspace/eastbourneart/media/myob/myob_customer.txt', 'w'), delimiter=',')
    spamWriter1 = csv.writer(open('/var/www/vhosts/eastbourneart.com.au/httpdocs/media/myob/myob_customer.txt', 'w'), delimiter=',')
    spamWriter.writerow(["Co./Last Name","First Name","Addr 1 - Line 1","           - Line 2","           - Line 3","           - Line 4","Invoice #","Date","Ship Via","Item Number","Quantity","price","Total","Inc-Tax Total","Non-GST Amount","GST Amount","Freight Amount"])
    spamWriter1.writerow(["Co./Last Name","First Name","Addr 1 - Line 1","           - Line 2","           - Line 3","           - Line 4","           - City","           - State","           - Postcode","           - Country","           - Phone # 1","           - Phone # 2","           - Fax #","           - Email","           - Contact Name,A.B.N. "])
    for i,x in enumerate(orders):
        
        if x.user:
            p = x.user.get_profile()
            
            s = x.getProfileShipping()
            b = x.getProfileBilling()
            if temp.count(x.user.email)==0:
                temp.append(x.user.email) 
                spamWriter1.writerow([p.company,'',s.address,s.address2,s.address3,'','',s.state,s.postcode,s.country,p.phone,p.phone2,p.fax,x.user.email,p.abn])
            for po in x.productorder_set.all():
                spamWriter.writerow([p.company,'',s.address,s.address2,s.address3,'',x.getOrderNumber(),x.started.date(),'',po.product.title,po.quantity,po.getUnitPrice(),po.getTotalPrice(),po.getTotalTax(),'0.00',str(float(po.getTotalTax())-float(po.getTotalPrice())),x.getShippingCharged()])
            spamWriter.writerow([])
            
    
    c = RequestContext(request,{"orders":orders})
    return HttpResponse(t.render(c))


def category(request):
    t = loader.get_template("admin/shop/discountprice/category.html")
    category = Categories.objects.all()
    errors = ''
    rp = request.POST.copy()
    errors = rp.lists()
    if rp.get("_save",None):
        try:
            categoryid = int(rp.get('category',None))
            off = rp.get('off', None)
            wholesale_off = rp.get('wholesale_off', None)
            start = datetimeformat(rp.get("start_0",''),rp.get("start_1",''))
            end = datetimeformat(rp.get("end_0",''),rp.get("end_1",''))
            if start == 0 or end == 0:
                raise 
            if float(off) == 0.0 and float(wholesale_off) == 0.0:
                raise
            products = Product.objects.filter(category_now__id=categoryid)
           
            for x in products:
                dp = DiscountPrice()
                dp.product = x
                dp.price = float(x.price * (float(100)-float(off)) * 0.01)
                dp.wholesale_price = float(x.wholesale_price * (float(100)-float(wholesale_off)) * 0.01)
                dp.start = start
                dp.end = end
                dp.save() 
            return HttpResponseRedirect('../')
        except:
            errors = 'Please insert all required data'
            
    
    c = RequestContext(request,{"category":category,"errors":errors})
    
    return HttpResponse(t.render(c))

def delete(request):
    now = datetime.datetime.now()
    dp = DiscountPrice.objects.filter(end__lt = now).delete()
    return HttpResponseRedirect('../')
    
def sendmail(request):
    t = loader.get_template('admin/website/subscription/sendmail.html')

        
    
    ids = request.GET.get('ids',None)
    ids = ids.split(',')
    selected = Subscription.objects.filter(id__in = ids)
    result_headers = ['email name','send already']
    results = Email.objects.all()
    select_headers = ['email address', 'wholesale']
    emails = []
    rp = request.POST.copy()
    message = ''
    if rp:
        emails = rp.getlist('emails')
        emails = Email.objects.filter(id__in=emails)
        for x in emails:
            x.sendmail(subscribe=selected)
            x.send=True
            x.save()

        message = 'You have sent %s mails to %s email addresses' %(len(emails), len(ids))
        
    c = RequestContext(request,{'result_headers':result_headers, 'results':results,'selected':selected,'select_headers':select_headers,'message':message})
    return HttpResponse(t.render(c))

def addtocategory(request):
    t = loader.get_template('admin/shop/product/addtocategory.html')
    ids = request.GET.get('ids',None)
    ids = ids.split(',')
    selected = Product.objects.filter(id__in = ids)
    
    list_name = 'category'
    result_headers = ['category','priority','is active']
    results = Categories.objects.all()
    select_headers = ['product','code','category']
    rp = request.POST.copy()
    message = ''
    coupons = []
    oldids = []
    if rp:
        categorylist = rp.getlist(list_name)
        category = Categories.objects.filter(id__in=categorylist)
        for x in selected:
            oldids = [str(xx.id) for xx in x.category_now.all()]
            x.category_now.add(*listConverter(oldids,categorylist))
            x.save()
        message = 'You have add %s products to %s categories' %(len(selected), len(categorylist))
    c = RequestContext(request,{'result_headers':result_headers,'results':results,'selected':selected,'select_headers':select_headers,'message':message,'list_name':list_name})
    return HttpResponse(t.render(c))
            
def addtocoupon(request):
    t = loader.get_template('admin/shop/discountprice/addtocoupon.html')
    ids = request.GET.get('ids',None)
    ids = ids.split(',')
    selected = DiscountPrice.objects.filter(id__in = ids)
    
    list_name = 'coupons'
    result_headers = ['coupon name','coupon number','coupon codes','coupon used']
    results = Coupon.objects.all()
    select_headers = ['product','start','end','priceoff','wholesale priceoff','category']
    rp = request.POST.copy()
    message = ''
    coupons = []
    oldids = []
    if rp:
        coupons = rp.getlist(list_name)
        coupons = Coupon.objects.filter(id__in=coupons)
        for x in coupons:
            oldids = [str(xx.id) for xx in x.discountprice_set.all()]
            x.discountprice_set.add(*listConverter(oldids,ids))
            x.save()
        message = 'You have add %s discount price to %s coupons' %(len(listConverter(oldids,ids)), len(coupons))
    c = RequestContext(request,{'result_headers':result_headers,'results':results,'selected':selected,'select_headers':select_headers,'message':message,'list_name':list_name})
    return HttpResponse(t.render(c))

def listConverter(list1,list2):
    return [x for x in list2 if x not in list1]

def addbycsv(request):
    t = loader.get_template('admin/shop/product/addbycsv.html')
    rp = request.POST.copy()
    message = []
    number = 0
    sms = []
    total = 0
    if rp.get("productupload"):
        #file = rp.get("productfile", None)
        #path = '/home/chaol/workspace/eastbourneart/media/myob/product.csv'
        path = '/var/www/vhosts/eastbourneart.com.au/httpdocs/media/myob/product.csv'
        destination = open(path, 'wb+')
        try:
            chunk = request.FILES.get("productfile", None).chunks()
            for c in chunk:
                destination.write(c)
        except:
            message.append("Please choose file to upload first")
   
        destination.close()
       
        #message = path
        
        input = csv2input.csv2input(path)
      
            
            
        #message= input.title, input.data
        try:
            index = input.title.index('code')
        except:
            message.append("Error at line 1: Please make sure line 1 have 'code' column and no columns with the same name")
        
        
        for i, x in enumerate(input.data):
            
        
            
            p = Product.objects.filter(code=x[index])
            
            if p:
                p = p[0]
            else:
                p = Product()
       
            for ii,xx in enumerate(x):
                iterator = input.title[ii].strip().lower()
         
                if iterator == 'status':
                    try:
                        id = ProductStatus.objects.filter(status=xx)[0]
                        p.status = id
                        p.save()
                    except :
                        message.append("Error at line "+ str(i+2)+": please check 'status' column. \n")# + str(sys.exc_info()[1]) + ".\n" 
                        break
                elif iterator.find('category') != -1:
                    category = xx.split(',')
                    c = Categories.objects.filter(name__in = category)
                    if c:
                        p.category_now = c
                    else:
                        message.append("Warning at line "+ str(i+2)+": No category added. Please check 'category_now' column. \n")
                else:
                    p.__setattr__(iterator,xx)
            try:
                site = Site.objects.all()
                p.sites = site
                p.save()
                number +=1
            except:
                message.append('Saving problems at line ' + str(i+2) + "\n")
                break
        message.append('You have successfully added/modified %s products' % str(number))
            
    elif rp.get("imageupload"):
        
        #path = '/home/chaol/workspace/eastbourneart/media/myob/image.csv'
        path = '/var/www/vhosts/eastbourneart.com.au/httpdocs/media/myob/image.csv'
        destination = open(path, 'wb+')
        try:
            chunk = request.FILES.get("imagefile", None).chunks()
            for c in chunk:
                destination.write(c)
        except:
            sms.append('Please choose file to upload first')
        
        destination.close()
        
        input = csv2input.csv2input(path,type='image')
        try:
            index = input.title.index('code')
        except:
            sms.append("Error at line 1: Please make sure line 1 have 'code' column and no columns with the same name")
        
        for i, x in enumerate(input.data):
            p = Product.objects.filter(code=x[index])
            if p:
                p = p[0]
                api = p.productimage_set.all()
                if api:
                    for apii in api:
                        apii.image = 'images/a'
                        apii.save()
                    api.delete()
                    p.save()
            else:
                sms.append("error at line " + str(i+2) + ": This product is not exist, images not uploaded")
                continue
            
            for ii, xx in enumerate(x):
                if ii != index and xx:
                                            
                    try:
                        pi = ProductImage()
                        pi.product = p
                        pi.image = xx
                        pi.is_featured_image = True
                        pi.save()
                        total = total + 1
                    except:
                        sms.append('Saving problems at line ' + str(i+2) + "\n")
                        break
                
        
        sms.append('You have successfully added/modified %s images' % str(total)) 
    
        
    c = RequestContext(request,{'message':message,'sms':sms})
    return HttpResponse(t.render(c))


def datetimeformat(date,time):
    temp = 0
    result = date.split('-')+time.split(':')
    if len(result) == 6:
        temp = datetime.datetime(int(result[0]),int(result[1]),int(result[2]),int(result[3]),int(result[4]),int(result[5]))
    elif len(result) == 5:
        temp = datetime.datetime(int(result[0]),int(result[1]),int(result[2]),int(result[3]),int(result[4]),0)
    return temp       

from eastbourne.website.admin import *

def emails_app_index(request):
    t = loader.get_template('admin/emails_index.html')
    
    user = request.user
    has_module_perms = user.has_module_perms('website')
    app_dict = {}
    register = [[Email, EmailAdmin(Email,EmailAdmin)],[Subscription,SubscriptionAdmin(Subscription,SubscriptionAdmin)]]
    
    for model, model_admin in register:
       
        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'admin_url': '/admin/website/%s/' % model.__name__.lower(),
                    'perms': perms,
                }
                if app_dict:
                    app_dict['models'].append(model_dict),
                else:
                    # First time around, now that we know there's
                    # something to display, add in the necessary meta
                    # information.
                    app_dict = {
                        'name': 'CRM',
                        'app_url': '',
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }
    app_list = [app_dict]
    #app_list = [{'app_url': '', 'models': [{'perms': {'add': True, 'change': True, 'delete': True}, 'admin_url': '/admin/website/email/', 'name': 'Emails',},  {'perms': {'add': True, 'change': True, 'delete': True}, 'admin_url': '/admin/website/subscription/', 'name': 'Subscriptions',}], 'has_module_perms': True, 'name': u'Emails'}] 
    
    c= RequestContext(request,{'app_list':app_list})
    return HttpResponse(t.render(c))