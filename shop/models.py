'''
@author: chaol
'''

from django.db import models
from django.contrib.auth.models import User
from django.template import Context, loader
import string
import random
from random import shuffle
import httplib, urllib
from django.contrib.sites.models import Site
from eastbourne.userprofile.models import UserType, Country
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save,post_delete

from django.conf import settings
import math
import eastbourne
import eastbourne.helpers
#import eastbourne.common

#import filters
import datetime

from eastbourne.shop.shipping.AustraliaPostDomestic import AustraliaPostDomestic
from eastbourne.shop.shipping.AustraliaPostInternational import AustraliaPostInternational

class Categories(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images/")
    priority = models.IntegerField(default=0, help_text="Used to control ordering of categories, higher numbers show higher in the list")
    is_active = models.BooleanField(default=False)
    def __unicode__(self):
        if self.parent:
            return str(self.parent) + " > " + self.name
        return self.name
    
    def getName(self):
        return self.__unicode__()
    def getUrl(self):
        if self.slug:
            return "/shop/%s/" % self.slug
        else:
            return "/shop/%s/" % self.id
    def getChildren(self):
        return self.categories_set.filter(is_active=True).order_by("-priority","name")
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["-parent__id"]


class Category(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images/")
    priority = models.IntegerField(default=0, help_text="Used to control ordering of categories, higher numbers show higher in the list")
    is_active = models.BooleanField(default=False)
    def __unicode__(self):
        if self.parent:
            return str(self.parent) + " > " + self.name
        return self.name
    def getUrl(self):
        if self.slug:
            return "/shop/%s/" % self.slug
        else:
            return "/shop/%s/" % self.id
    def getChildren(self):
        return self.category_set.filter(is_active=True).order_by("-priority","name")
    
    class Meta:
        verbose_name_plural = "Categories"
        

class TaxRate(models.Model):
    name = models.CharField(max_length=255)
    rate = models.FloatField()
    countries = models.ManyToManyField(Country)
    is_default = models.BooleanField()
    def __unicode__(self):
        return self.name+" "+str(self.rate)

class ShippingDiscount(models.Model):
    name = models.CharField(max_length=255)
    off = models.FloatField(default=0,help_text='%')
    country = models.ForeignKey(Country,null=True,blank=True,editable=False)
    def __unicode__(self):
        return self.name
    def getRatio(self):
        return float(100-self.off)/float(100)
    
class ShippingManagement(models.Model):
    name = models.CharField(max_length=255)
    #domain = models.ForeignKey(Site)
    api = models.CharField(max_length=50, verbose_name='method', choices=(("aupost", "Australia Post(api)"),('weight','Weight Based'),('price','Price Based',)))
    free_shipping = models.FloatField(blank=True,null=True,help_text='shipping free if total amount(inc gst) above the value here')
    minimum_shipping = models.FloatField(blank=True,null=True,help_text='minimum shipping price allowed')
    maximum_shipping = models.FloatField(blank=True,null=True, help_text='maximum shipping price allowed')
    fixed_shipping = models.FloatField(blank=True,null=True,help_text='if value here, shipping will always be this amount no matter what the method is')
    countries = models.ManyToManyField(Country)
    wholesale = models.BooleanField(default=False,editable=False)
    gold = models.BooleanField("use this for all the rest countries",default=False)
    
    
    def __unicode__(self):
        return self.name
    
    def getBasePrice(self,num):

        for x in self.shippingbased_set.all():
            if num >= x.range_from and num <= x.range_to:
                return x
            
    def display_countries(self):
        return ','.join([x.country for x in self.countries.all()])

class ShippingBased(models.Model):
    shipping = models.ForeignKey(ShippingManagement)
    range_from = models.FloatField(help_text='weight(g), price($)')
    range_to = models.FloatField(help_text='weight(g), price($)')
    amount = models.FloatField(help_text='$')
    
    def __unicode__(self):
        return self.shipping.name
    
    class Meta:
        ordering = ['shipping', 'range_from']  
    
class Size(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=12, help_text="This will be appended to the product (eg. XL)")
    def __unicode__(self):
        return self.name

class Style(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=12, help_text="This will be appended to the product (eg. BLACK)")
    def __unicode__(self):
        return self.name

class ProductStatus(models.Model):
    status = models.CharField(max_length=50)
    display_to_user = models.BooleanField(default=True)
    can_buy = models.BooleanField(default=True)
    def __unicode__(self):
        return self.status
    class Meta:
        verbose_name_plural = "Product Status"


class Product(models.Model):
    title = models.CharField(max_length=255)
    title.alphabetic_filter = True
    code = models.SlugField(unique=True)
    description = models.TextField(help_text="Maximum of 120 characters")
    price = models.FloatField("Tax free price", default=0.00, help_text="If price is 0.00 then it will be unavailable to retail customers")
    wholesale_price = models.FloatField("Wholesale tax free price", default=0.00, help_text="If price is 0.00 then it will be unavailable to wholesalers")
    minimum_quantity = models.IntegerField(default=1)
    minimum_quantity_wholesale = models.IntegerField(default=1)
    maximum_quantity = models.IntegerField(default=20)
    maximum_quantity_wholesale = models.IntegerField(default=20)
    tax_rate = models.ForeignKey(TaxRate, blank=True, null=True, related_name="retail_tax")
    wholesale_tax_rate = models.ForeignKey(TaxRate, blank=True, null=True, related_name="wholesale_tax")
    sizes = models.ManyToManyField(Size, editable=False,blank=True, null=True)
    styles = models.ManyToManyField(Style, blank=True, null=True)
    category = models.ForeignKey(Category, editable=False, blank=True, null=True)
    category_now = models.ManyToManyField(Categories)
    sites = models.ManyToManyField(Site, default=Site.objects.all())
    status = models.ForeignKey(ProductStatus)
    related_products = models.ManyToManyField('self', blank=True, null=True)
    weight = models.IntegerField(default=1, help_text="the weight of the product in grams")
    length = models.IntegerField(default=1, help_text="the length of the product in cm")
    width =  models.IntegerField(default=1, help_text="the width of the product in cm")
    height =  models.IntegerField(default=1, help_text="the height of the product in cm")
    inventory =  models.IntegerField(blank=True,null=True, help_text="leave it empty if inventory is not important for the product")
    class Meta:
        ordering = ['code']

    
    def __unicode__(self):
        return self.code+" "+self.title
    
    def getCategory(self):
        a = []
        categories = self.category_now.all()
        for x in categories:
            a.append(unicode(x))
        
        return ', '.join(a)
        
    def getWholesaleTax(self):
        if self.wholesale_tax_rate == None:
            return 1
        else:
            return self.wholesale_tax_rate.rate
    def getTax(self):
        if self.tax_rate == None:
            return 1
        else:
            return self.tax_rate.rate
    

    
        
    def isDiscounted(self,wholesale=False):
        return self.getCurrentPrice("",wholesale) != self.getNormalPrice(wholesale)
    def isDiscountedW(self, wholesale=True):
        return self.getCurrentPrice("",wholesale) != self.getNormalPrice(wholesale)
    def getNormalPrice(self, wholesale=False):
        if not wholesale:
            return eastbourne.helpers.formatCurrency(self.price)
        else:
            return eastbourne.helpers.formatCurrency(self.wholesale_price)
    def getNormalTaxPrice(self, wholesale=False):
        # TODO get the proper tax rate
        return eastbourne.helpers.formatCurrency(float(self.getNormalPrice(wholesale)))
    def getNormalTaxPriceW(self):
        # TODO get the proper tax rate
        return eastbourne.helpers.formatCurrency(float(self.getNormalPrice(True)))
    
    '''------------------------------------------------------------------'''
    def getFirstPrice(self, wholesale,coupon):
        psp = self.productsizeprice_set.all()
        if psp:
            size = psp[0].size
            
            return eastbourne.helpers.formatCurrency(self.getCurrentRightPrice(size, wholesale, coupon))
    
    
    def getCurrentRightPrice(self,size,wholesale,couponcode):
        now = datetime.datetime.now()
        coupon = Coupon.objects.all()
        
        r = None
        
        result =  [x if x.checkCode(couponcode) else None for x in coupon]
        for x in result:
            if x != None:
                r = x
                break 
        dp = DiscountPrice.objects.filter(product=self, start__lte=now, end__gt=now, coupon=r).order_by("-start")
        if not dp:
            dp = DiscountPrice.objects.filter(product=self, start__lte=now, end__gt=now,coupon=None).order_by("-start")
        
        psp = []
        if size:
            psp = self.productsizeprice_set.filter(size__name=size)
        
        if wholesale:
            if dp and dp[0].wholesale_price > 0:
                if psp and psp[0].wholesale_price > 0:
                    ratio = float(dp[0].wholesale_price)/float(self.getNormalPrice(wholesale))
                    return eastbourne.helpers.formatCurrency(psp[0].wholesale_price*ratio) 
                else:
                    return eastbourne.helpers.formatCurrency(dp[0].wholesale_price)
            else:
                if psp and psp[0].wholesale_price > 0:
                    return eastbourne.helpers.formatCurrency(psp[0].wholesale_price)
                else:
                    return eastbourne.helpers.formatCurrency(self.wholesale_price)
        else:
            if dp and dp[0].price > 0:
                if psp and psp[0].price > 0:
                    ratio = float(dp[0].price)/float(self.getNormalPrice(wholesale))
                    return eastbourne.helpers.formatCurrency(psp[0].price*ratio) 
                else:
                    return eastbourne.helpers.formatCurrency(dp[0].price)
            else:
                if psp and psp[0].price > 0:
                    return eastbourne.helpers.formatCurrency(psp[0].price)
                else:
                    return eastbourne.helpers.formatCurrency(self.price)
                
    '''-----------------------------------------------------------------'''
    
    def getCurrentPrice(self, size="",wholesale=False):
        now = datetime.datetime.now()
        dp = DiscountPrice.objects.filter(product=self, start__lte=now, end__gt=now).order_by("-start")
        psp = self.productsizeprice_set.filter(size__name=size)
        if wholesale:
            if dp and dp[0].wholesale_price > 0:
                return eastbourne.helpers.formatCurrency(dp[0].wholesale_price)
            else:
                if psp and psp[0].wholesale_price > 0:
                    return eastbourne.helpers.formatCurrency(psp[0].wholesale_price)
                else:
                    return eastbourne.helpers.formatCurrency(self.wholesale_price)
        else:
            if dp and dp[0].price > 0:
                return eastbourne.helpers.formatCurrency(dp[0].price)
            else:
                if psp and psp[0].price > 0:
                    return eastbourne.helpers.formatCurrency(psp[0].price)
                else:
                    return eastbourne.helpers.formatCurrency(self.price)
                
    def getCurrentPriceW(self, size="",wholesale=True):
        now = datetime.datetime.now()
        dp = DiscountPrice.objects.filter(product=self, start__lte=now, end__gt=now).order_by("-start")
        psp = self.productsizeprice_set.filter(size__name=size)
        if wholesale:
            if dp and dp[0].wholesale_price > 0:
                return eastbourne.helpers.formatCurrency(dp[0].wholesale_price)
            else:
                if psp and psp[0].wholesale_price > 0:
                    return eastbourne.helpers.formatCurrency(psp[0].wholesale_price)
                else:
                    return eastbourne.helpers.formatCurrency(self.wholesale_price)
        else:
            if dp and dp[0].price > 0:
                return eastbourne.helpers.formatCurrency(dp[0].price)
            else:
                if psp and psp[0].price > 0:
                    return eastbourne.helpers.formatCurrency(psp[0].price)
                else:
                    return eastbourne.helpers.formatCurrency(self.price)
                
    def getTaxFreePrice(self,size, wholesale,coupon):
        return eastbourne.helpers.formatCurrency(self.getCurrentRightPrice(size,wholesale,coupon))
    def getTaxPrice(self, wholesale=False):
        # TODO get the proper tax rate
       
        return eastbourne.helpers.formatCurrency(float(self.getCurrentPrice("",wholesale)))
    
    def getTaxPriceW(self,wholesale=True):
        
        return eastbourne.helpers.formatCurrency(float(self.getCurrentPrice("",wholesale)))
    
    def getRelatedProducts(self, wholesale=False):
        # this needs to be filtered further for permissions
        products = self.related_products.distinct().filter(sites__pk=settings.SITE_ID, status__display_to_user=True,category_now__is_active=True)
        if wholesale:
            products = products.filter(wholesale_price__gt=0)
        else:
            products = products.filter(price__gt=0)
        p = list(products)
        shuffle(p)
        return p
    def getFeaturedImage(self):
        featured = self.productimage_set.filter(is_featured_image=True)
        try:
            if featured:
                return featured[0]
            else:
                return self.getImages()[0]
        except:
            return None
    def getImages(self):
        return self.productimage_set.all().order_by("-is_featured_image", "id")

class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to="images/")
    title = models.CharField(max_length=255, blank=True, null=True)
    is_featured_image = models.BooleanField(default=False, help_text="Use this as a featured image for a product")
    def __unicode__(self):
        return self.product.title

class PackageProduct(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    def __unicode__(self):
        return self.status

class Package(models.Model):
    products = models.ManyToManyField(PackageProduct)
    
class Coupon(models.Model):
    name = models.CharField(max_length=255,unique=True)
    number = models.IntegerField(editable=False,blank=True,null=True)
    codes = models.CharField(max_length=255)
    used = models.TextField(editable=False,blank=True,null=True)
    
    def __unicode__(self):
        return self.name
    
    def checkCode(self,code):
        now = datetime.datetime.now()
        dps = self.discountprice_set.filter(start__lte = now, end__gt = now,coupon=self)
        if self.codes.strip()==code.strip() and dps:
            return True
        return False
    
    '''def addUsed(self,code):
        if self.used:
            used = self.used.split(',')
        else:
            used = []
        used.append(code)
        self.used = ','.join(used)
        self.save()
        
    def save(self):
        if not self.codes:
            
            self.codes = getRandom(self.number)
        else:
            length = len(self.codes.split(','))
            if length < self.number:
                number = self.number - length
                self.codes = getRandom(number,self.codes.split(','))
            else:
                if self.used:
                    temp = [x for x in self.codes.split(',') if x not in self.used.split(',')]
                    self.codes = ','.join((self.used.split(',')+temp)[:self.number])
                else:
                    self.codes=','.join(self.codes.split(',')[:self.number])
                
        super(Coupon,self).save()'''


class DiscountPrice(models.Model):
    product = models.ForeignKey(Product)
    price = models.FloatField(default=0.0)
    wholesale_price = models.FloatField(default=0.0)
    coupon = models.ManyToManyField(Coupon, blank=True,null=True)
    start = models.DateTimeField(default=datetime.datetime.now())
    end = models.DateTimeField(default=datetime.datetime.now())
    def __unicode__(self):
        return unicode(self.product)
    
    def getCategory(self):
        return self.product.getCategory()
    
    def getPrice(self, wholesale):
        return eastbourne.helpers.formatCurrency(self.wholesale_price) if wholesale else eastbourne.helpers.formatCurrency(self.price)
        
    
    def priceoff(self):
        if self.product.price != 0:
            percentage = (1-float(self.price)/float(self.product.price)) * 100
        else:
            percentage = 0
        return "%.2f" % percentage + '%'
    #getCategory.admin_order_field = 'product__category_now'
    def wholesale_priceoff(self):
        if self.product.wholesale_price != 0:
            percentage = (1-float(self.wholesale_price)/float(self.product.wholesale_price)) * 100
        else:
            percentage = 0
        return "%.2f" % percentage + '%'
    
    def pricecut(self,wholesale):
        return self.wholesale_priceoff() if wholesale else self.priceoff
    
    def coupon_name(self):
        return ','.join([x.name for x in self.coupon.all()])
            

class DiscountedPriceSize(models.Model):
    product = models.ForeignKey(DiscountPrice)
    size = models.ForeignKey(Size)
    price = models.FloatField(default=0.0)
    wholesale_price = models.FloatField(default=0.0)
    

class OrderStatus(models.Model):
    status = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "Order Status"
    def __unicode__(self):
        return self.status



class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    status = models.ForeignKey(OrderStatus)
    started = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_wholesale = models.BooleanField(default=False)
    shipping_charged = models.FloatField(default=0.00)
    tax_charged = models.FloatField(default=0.00)
    total_charged = models.FloatField(default=0.00)
    coupon = models.TextField(editable=False,blank=True, null=True)
    def __unicode__(self):
        try:
            return self.getOrderNumber() + " " + str(self.user)+" "+str(self.started)+" price: $"+str(self.total_charged)+" items: "+str(self.getTotalItems())+" " 
        except:
            return "?"
        
  #  def getBoxes(self):
  #      weight = self.getTotalWeight()
  #      
  #      boxValume = float(35*46*24*0.95)#TO CHANGE
  #      sum = 0 
  #      for x in self.productorder_set.all():
  #          sum = sum + x.getValume()
  #          
  #      box = int(math.ceil(sum/boxValume))
  #      box_least = int(math.ceil(weight/20000.0))
  #      if box >= box_least:
  #          return box
  #      else:
  #          return box_least
    
  #  def getBoxWeight(self):
  #      return float(self.getTotalWeight()/self.getBoxes())

    def user_detail(self):
        try:
            return "<b>%s</b> -- %s %s" %(self.user.get_profile().company, self.user.first_name, self.user.last_name) if self.is_wholesale else "%s %s" %(self.user.first_name, self.user.last_name)
        except:
            return self.user
        
    user_detail.allow_tags = True
        
    def coupon_used(self):
        po = self.productorder_set.all()
        return ','.join([x.coupon for x in po if x.coupon != None])
        
    def getOrderNumber(self):
        return "EB"+str(self.id).zfill(4)
    def formatNumber(self):
        try:
            return "EB"+str(self.id).zfill(4)
        except Exception, e:
            return e
    def getShippingCharged(self):
        return eastbourne.helpers.formatCurrency(self.shipping_charged)
    def getTaxCharged(self):
        return eastbourne.helpers.formatCurrency(self.tax_charged)
    def getTotalCharged(self):
        return eastbourne.helpers.formatCurrency(self.total_charged)
    def getTotalItems(self):
        try:
            return sum([x.quantity for x in self.productorder_set.all()])
        except:
            return 0
    def getTotalWeight(self):
        items = []
        for x in self.productorder_set.all():
            if x.product.weight:
                items.append(x.quantity*x.product.weight)
        return sum(items)
    def getTotalTaxFreePrice(self):
        try:
            price = sum([float(x.getUnitPrice())*float(x.quantity) for x in self.productorder_set.all()])
            return eastbourne.helpers.formatCurrency(price)
        except Exception:
            return 0
    def getTotalGST(self):
#        FIXME need to calculate proper tax rate
        try:
            price = sum([float(x.getTotalTax()) for x in self.productorder_set.all()])
        except Exception:
            return 0
        return eastbourne.helpers.formatCurrency(float(price) - float(self.getTotalTaxFreePrice()))
  #  def getShippingCost(self):
  #      try:
  #          profile = self.user.get_profile()
  #          shipping = profile.shipping_set.all()[0]
  #          if shipping.country.country.strip().lower() == 'australia':
  #              return eastbourne.helpers.formatCurrency(float(postAustralia(self.getBoxes(),self.getBoxWeight(),shipping.postcode)))
  #          else:
  #              return eastbourne.helpers.formatCurrency(float(calculateshipping(shipping.country.country, shipping.postcode, self.getTotalWeight())))
  #      except Exception, e:
  #          #raise ValueError(e)
  #         return 0.00
  #  def getTotalPrice(self):
  #      return eastbourne.helpers.formatCurrency(float(self.getTotalGST())+float(self.getTotalTaxFreePrice())+float(self.getShippingCost()))
    def getProfile(self):
        try:
            return self.user.get_profile()
        except:
            return None
    def getProfileShipping(self):
        try:
            return self.user.get_profile().shipping_set.all()[0]
        except:
            return None
    def getProfileBilling(self):
        try:
            return self.user.get_profile().billing_set.all()[0]
        except:
            return None
        
    def getTotal(self):
        try:
            price = sum([float(x.getTotalTax()) for x in self.productorder_set.all()])
        except Exception:
            return 0
        
        return price
    
    def save(self):
        if self.user and self.user.is_active:
            self.is_wholesale = True
            self.total_charged = self.tax_charged + self.shipping_charged + float(self.getTotalTaxFreePrice())  
        else:
            self.is_wholesale = False
            
            self.shipping_charged = float(getShippingCost(self))
            self.total_charged = self.getTotal()+ self.shipping_charged
        
        if self.id:
            origin = Order.objects.get(id=self.id)
            if self.status != origin.status:    
                if self.user and self.status.status == 'Shipped':
                    profile = self.user.get_profile()
                    shipping = profile.shipping_set.all()
                    billing = profile.billing_set.all()
                    billing = billing[0] if billing else shipping[0]
                    if self.user and self.user.is_active:
                        payment = False
                    else:
                        payment = True
                    t = loader.get_template('orderconfirmationemail.html')
                    d = {"profile":profile, "shipping":shipping[0], "billing":billing,'payment':payment,'order':self}
                    c = Context(d)
                    msg = t.render(c)
                    email = EmailMultiAlternatives('EASTBOURNEART Order Shipped - Order '+ self.getOrderNumber(), msg, 'no-reply@eastbourneart.com.au', [self.user.email])
                    email.attach_alternative(msg, "text/html")
                    email.send()

        super(Order, self).save()
        
class ProductSizePrice(models.Model):
    product = models.ForeignKey(Product)
    size = models.ForeignKey(Size)
    price = models.FloatField("Tax Free", default=0.00)
    wholesale_price = models.FloatField("Wholesale Price", default=0.00)
    def __unicode__(self):
        return str(self.price) 


class ProductOrder(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    price = models.FloatField("Unit Price", default=0.00)
    size = models.ForeignKey(Size, blank=True, null=True)
    style = models.ForeignKey(Style, blank=True, null=True)
    coupon = models.CharField(max_length=255,editable=False, blank=True, null=True)
 
    
    def __unicode__(self):
        if self.order.is_wholesale:
            return "title: " + str(self.product.title)+" price: "+str(self.product.getCurrentPrice(self.size,True)) + " tax:" + str((float(self.product.getWholesaleTax())-1)*float(self.product.getCurrentPrice(self.size,True))) + " min qty:" + str(self.product.minimum_quantity_wholesale) + " max qty:" + str(self.product.maximum_quantity_wholesale)
        else:
            return "title: " + str(self.product.title)+" price:" +str(self.product.getCurrentPrice(self.size,False)) + " tax:" + str((float(self.product.getTax())-1)*float(self.product.getCurrentPrice(self.size,False)))+ " min qty:" + str(self.product.minimum_quantity) + " max qty:" + str(self.product.maximum_quantity)
    def code(self):
        s = self.product.code
        if self.size:
            s = s + "-%s" % self.size.code
        if self.style:
            s = s + "-%s" % self.style.code
        return s
    
    def getValume(self):
        valume = float(self.product.height*self.product.width*self.product.length)
        valume = float(valume * self.quantity)
        return valume
    
    
    def getCategory(self):
        category = self.product.getCategory()
        return category
    def getOrderNumber(self):
        return self.order.getOrderNumber()
    
    def getOrderStatus(self):
        return self.order.status
    
    def getUnitPrice(self):
        return eastbourne.helpers.formatCurrency(self.price)
    def getTotalTax(self):
        if self.order.is_wholesale:
            if self.product.wholesale_tax_rate != None:
                unitPrice = self.product.wholesale_tax_rate.rate * self.price
            else:
                unitPrice = self.price
        else:
            if self.product.tax_rate != None:
                unitPrice = self.product.tax_rate.rate * self.price
            else:
                unitPrice = self.price
            
        price = unitPrice * self.quantity
        return eastbourne.helpers.formatCurrency(price)
        
    def getTotalPrice(self):
        if not self.price:
            self.price = self.product.price
            self.save()
        return eastbourne.helpers.formatCurrency(self.price * self.quantity)
    def save(self):
        self.quantity = int(self.quantity)
        if self.order and self.order.user and self.order.user.is_active:
            if self.quantity > self.product.maximum_quantity_wholesale:
                self.quantity = self.product.maximum_quantity_wholesale
            elif self.quantity < self.product.minimum_quantity_wholesale:
                self.quantity = self.product.minimum_quantity_wholesale
        else:
            if self.quantity > self.product.maximum_quantity:
                self.quantity = self.product.maximum_quantity
            elif self.quantity < self.product.minimum_quantity:
                self.quantity = self.product.minimum_quantity
        super(ProductOrder, self).save()
def calculateshipping(country, postcode, weight):
    if country.strip().lower() == "australia":
        if not postcode:
            raise ValueError("Postcode is required")
        else:
            m = AustraliaPostDomestic()
            zone = m.findZone(int(postcode))
    else:
        m = AustraliaPostInternational()
        zone = m.findZone(country)
    weight = int(weight)
    if not weight:
        raise ValueError("Weight is required")
    if not zone:
        raise ValueError("Unable to calculate Freight & Handling, please continue with your order, we will contact you to arrange for postage")
    price = m.calculate(zone, weight)
    return price

'''def postAustralia(quantity, weight, postcode):
    params = urllib.urlencode({"Quantity":int(quantity),'Service_Type':'STANDARD','Height':350,'Width':240,'Length':460,'Weight':int(weight),'country':'AU','Destination_Postcode':'2159','Pickup_Postcode':postcode})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("drc.edeliver.com.au")
    conn.request("POST", "/ratecalc.asp", params, headers)
    response = conn.getresponse()
    data = response.read()
    datas = data.split('\n')
    datass = datas[0].split('=')
    price = float(datass[1])
    #------------------------shipping discount--------------
    sd = ShippingDiscount.objects.all()
    sd = sd[0] if sd else None
    price = price * sd.getRatio() if sd else price
    
    #------------------------shipping discount--------------#
    return price

def postInternational(quantity,weight,postcode,country):
    countries = {'samoa': 'WS', 'japan': 'JP', 'french southern territories': 'TF', 'tokelau': 'TK', 'korea, republic of': 'KR', 'iran, islamic republic of': 'IR', 'azerbaijan': 'AZ', 'uzbekistan': 'UZ', 'djibouti': 'DJ', 'seychelles': 'SC', 'french guiana': 'GF', 'malta': 'MT', 'guinea-bissau': 'GW', 'hungary': 'HU', 'cyprus': 'CY', 'barbados': 'BB', 'bhutan': 'BT', 'lithuania': 'LT', 'mongolia': 'MN', 'andorra': 'AD', 'tunisia': 'TN', 'rwanda': 'RW', 'aruba': 'AW', 'puerto rico': 'PR', 'argentina': 'AR', 'norway': 'NO', 'sierra leone': 'SL', 'somalia': 'SO', 'ghana': 'GH', 'belarus': 'BY', 'cuba': 'CU', 'zambia': 'ZM', 'french polynesia': 'PF', 'guatemala': 'GT', 'isle of man': 'IM', 'syrian arab republic': 'SY', 'belgium': 'BE', 'haiti': 'HT', 'kazakhstan': 'KZ', 'burkina faso': 'BF', 'liberia': 'LR', 'kyrgyzstan': 'KG', 'netherlands': 'NL', 'kuwait': 'KW', 'denmark': 'DK', 'philippines': 'PH', 'montserrat': 'MS', 'senegal': 'SN', 'tristan da cunha': 'SH', 'congo': 'CG', 'croatia': 'HR', 'bosnia': 'BA', 'chad': 'TD', 'switzerland': 'CH', 'mali': 'ML', 'bulgaria': 'BG', 'jamaica': 'JM', 'albania': 'AL', 'angola': 'AO', 'lebanon': 'LB', 'american samoa': 'AS', 'malaysia': 'MY', 'falkland islands (malvinas)': 'FK', 'christmas island': 'CX', 'mozambique': 'MZ', 'micronesia, federated states of': 'FM', 'greece': 'GR', 'tanzania, united republic of': 'TZ', 'nicaragua': 'NI', 'new zealand': 'NZ', 'brazil': 'BR', 'afghanistan': 'AF', 'qatar': 'QA', 'palau': 'PW', 'turkmenistan': 'TM', 'equatorial guinea': 'GQ', 'pitcairn': 'PN', 'guinea': 'GN', 'panama': 'PA', 'nepal': 'NP', 'central african republic': 'CF', 'luxembourg': 'LU', 'solomon islands': 'SB', 'latvia': 'LV', 'cook islands': 'CK', 'tuvalu': 'TV', 'netherlands antilles': 'AN', 'namibia': 'NA', 'nauru': 'NR', 'russian federation': 'RU', 'british indian ocean territory': 'IO', 'united arab emirates': 'AE', 'south georgia and the south sandwich islands': 'GS', 'saint kitts and nevis': 'KN', 'sri lanka': 'LK', 'paraguay': 'PY', 'china': 'CN', 'armenia': 'AM', 'kiribati': 'KI', 'belize': 'BZ', 'palestinian territory, occupied': 'PS', 'cayman islands': 'KY', 'yemen': 'YE', 'northern mariana islands': 'MP', 'trinidad and tobago': 'TT', 'mayotte': 'YT', 'gambia': 'GM', 'finland': 'FI', 'saint pierre and miquelon': 'PM', 'mauritius': 'MU', 'antigua and barbuda': 'AG', 'niue': 'NU', 'dominican republic': 'DO', "cote d'ivoire": 'CI', 'jersey': 'JE', 'suriname': 'SR', 'pakistan': 'PK', 'romania': 'RO', 'reunion': 'RE', 'czech republic': 'CZ', 'myanmar': 'MM', 'el salvador': 'SV', 'egypt': 'EG', 'guam': 'GU', 'papua new guinea': 'PG', 'united states': 'US', 'austria': 'AT', 'greenland': 'GL', 'colombia': 'CO', 'thailand': 'TH', 'honduras': 'HN', 'niger': 'NE', 'fiji': 'FJ', 'comoros': 'KM', 'turkey': 'TR', 'united kingdom': 'GB', 'madagascar': 'MG', 'iraq': 'IQ', 'bangladesh': 'BD', 'mauritania': 'MR', 'saint barth\xc3\xa9lemy': 'BL', 'uruguay': 'UY', 'france': 'FR', 'bahamas': 'BS', 'slovakia': 'SK', 'gibraltar': 'GI', 'ireland': 'IE', 'nigeria': 'NG', 'anguilla': 'AI', 'malawi': 'MW', 'ecuador': 'EC', 'moldova, republic of': 'MD', 'ukraine': 'UA', 'israel': 'IL', 'congo, the democratic republic of the': 'CD', 'peru': 'PE', 'algeria': 'DZ', 'serbia': 'RS', 'montenegro': 'ME', 'tajikistan': 'TJ', 'svalbard and jan mayen': 'SJ', 'togo': 'TG', 'holy see (vatican city state)': 'VA', 'jordan': 'JO', 'chile': 'CL', 'martinique': 'MQ', 'oman': 'OM', 'turks and caicos islands': 'TC', 'virgin islands, british': 'VG', 'spain': 'ES', 'sao tome and principe': 'ST', 'georgia': 'GE', 'bouvet island': 'BV', 'vietnam': 'VN', 'brunei darussalam': 'BN', 'morocco': 'MA', 'sweden': 'SE', 'heard island and mcdonald islands': 'HM', 'gabon': 'GA', 'guyana': 'GY', 'macedonia, the former yugoslav republic of': 'MK', 'grenada': 'GD', 'guadeloupe': 'GP', 'hong kong': 'HK', 'bahrain': 'BH', "korea, democratic people's republic of": 'KP', 'estonia': 'EE', 'mexico': 'MX', 'india': 'IN', 'new caledonia': 'NC', 'lesotho': 'LS', 'antarctica': 'AQ', 'australia': 'AU', 'saint vincent and the grenadines': 'VC', 'uganda': 'UG', 'burundi': 'BI', 'kenya': 'KE', 'macao': 'MO', 'botswana': 'BW', 'saint martin (french part)': 'MF', 'italy': 'IT', 'western sahara': 'EH', 'south africa': 'ZA', 'cambodia': 'KH', 'ethiopia': 'ET', 'swaziland': 'SZ', 'bermuda': 'BM', 'timor-leste': 'TL', 'vanuatu': 'VU', 'marshall islands': 'MH', 'cameroon': 'CM', 'benin': 'BJ', 'canada': 'CA', "lao, people's democratic republic": 'LA', 'saudi arabia': 'SA', 'singapore': 'SG', 'faroe islands': 'FO', 'iceland': 'IS', 'saint lucia': 'LC', 'monaco': 'MC', 'virgin islands, u.s.': 'VI', 'costa rica': 'CR', 'venezuela': 'VE', 'united states minor outlying islands': 'UM', 'cocos (keeling) islands': 'CC', 'slovenia': 'SI', 'germany': 'DE', '\xc3\x85land islands': 'AX', 'wallis and futuna': 'WF', 'san marino': 'SM', 'dominica': 'DM', 'libyan, arab jamahiriya': 'LY', 'eritrea': 'ER', 'tonga': 'TO', 'maldives': 'MV', 'norfolk island': 'NF', 'poland': 'PL', 'indonesia': 'ID', 'cape verde': 'CV', 'taiwan': 'TW', 'sudan': 'SD', 'liechtenstein': 'LI', 'zimbabwe': 'ZW', 'portugal': 'PT', 'guernsey': 'GG', 'bolivia': 'BO','ascension island': 'AC','east timor': 'TP'}
    if countries.has_key(country.strip().lower()):
        params = urllib.urlencode({"Quantity":int(quantity),'Service_Type':'AIR','Height':350,'Width':240,'Length':460,'Weight':int(weight),'country':countries[country.strip().lower()],'Destination_Postcode':'2159','Pickup_Postcode':postcode})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("drc.edeliver.com.au")
        conn.request("POST", "/ratecalc.asp", params, headers)
        response = conn.getresponse()
        data = response.read()
        datas = data.split('\n')
        datass = datas[0].split('=')
        price = float(datass[1])
        if price == 0:
            raise ValueError("Sorry, unable to calculate Freight & Handling, please continue with your order, we will contact you to arrange for postage")
        else:
            #------------------------shipping discount--------------
            sd = ShippingDiscount.objects.all()
            sd = sd[0] if sd else None
            price = price * sd.getRatio() if sd else price
    
            #------------------------shipping discount--------------
            return price
    else:
        raise ValueError("Sorry, unable to calculate Freight & Handling, please continue with your order, we will contact you to arrange for postage")'''#return calculateshipping(country, postcode, weight)

def postAustralia(quantity, weight, postcode,orderprice, type='random'):
    c = Country.objects.filter(country__iexact = 'australia')
    c = c[0] if c else ''
    if type == 'random':
        shipping = ShippingManagement.objects.filter(countries=c,gold=False) if c else None
    elif type == 'wholesale':
        shipping = ShippingManagement.objects.filter(countries=c,wholesale=True) if c else None
    else:
        shipping = ShippingManagement.objects.filter(id=type)
    if not shipping:
        shipping = ShippingManagement.objects.filter(countries=c,gold=True) if c else None    
        
    if not shipping:
        raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
    
    '''---------------------fixed shipping------------------------'''
    if shipping and shipping[0].fixed_shipping:
        return shipping[0].fixed_shipping
    '''---------------------fixed shipping-----------------------'''
    '''---------------------free shipping------------------------'''
    if shipping and shipping[0].free_shipping and orderprice > shipping[0].free_shipping:
        return 'free'
    '''---------------------free shipping------------------------'''
    if shipping[0].api == 'aupost':
        params = urllib.urlencode({"Quantity":int(quantity),'Service_Type':'STANDARD','Height':350,'Width':240,'Length':460,'Weight':int(weight),'country':'AU','Destination_Postcode':'2159','Pickup_Postcode':postcode})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("drc.edeliver.com.au")
        conn.request("POST", "/ratecalc.asp", params, headers)
        response = conn.getresponse()
        data = response.read()
        datas = data.split('\n')
        datass = datas[0].split('=')
        price = float(datass[1])
        if price == 0:
            raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
    
    elif shipping and shipping[0].api == 'weight':
        baseprice = shipping[0].getBasePrice(weight*quantity)
        if baseprice:
            price = baseprice.amount
        else:
            raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
    elif shipping and shipping[0].api == 'price':
        baseprice = shipping[0].getBasePrice(orderprice)
        if baseprice:
            price = baseprice.amount
        else:
            raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
    else:
        price = None

    '''-----------------------------minimum maximum price -----------------------------'''
    if price and shipping and shipping[0].minimum_shipping and price < shipping[0].minimum_shipping:
        price = shipping[0].minimum_shipping
    elif price and shipping and shipping[0].maximum_shipping and price > shipping[0].maximum_shipping:
        price = shipping[0].maximum_shipping
    '''-----------------------------minimum maximum price -----------------------------'''
    return 'free' if price == 0 else price 

def postInternational(quantity,weight,postcode,country,orderprice, type='random'):
    countries = {'samoa': 'WS', 'japan': 'JP', 'french southern territories': 'TF', 'tokelau': 'TK', 'korea, republic of': 'KR', 'iran, islamic republic of': 'IR', 'azerbaijan': 'AZ', 'uzbekistan': 'UZ', 'djibouti': 'DJ', 'seychelles': 'SC', 'french guiana': 'GF', 'malta': 'MT', 'guinea-bissau': 'GW', 'hungary': 'HU', 'cyprus': 'CY', 'barbados': 'BB', 'bhutan': 'BT', 'lithuania': 'LT', 'mongolia': 'MN', 'andorra': 'AD', 'tunisia': 'TN', 'rwanda': 'RW', 'aruba': 'AW', 'puerto rico': 'PR', 'argentina': 'AR', 'norway': 'NO', 'sierra leone': 'SL', 'somalia': 'SO', 'ghana': 'GH', 'belarus': 'BY', 'cuba': 'CU', 'zambia': 'ZM', 'french polynesia': 'PF', 'guatemala': 'GT', 'isle of man': 'IM', 'syrian arab republic': 'SY', 'belgium': 'BE', 'haiti': 'HT', 'kazakhstan': 'KZ', 'burkina faso': 'BF', 'liberia': 'LR', 'kyrgyzstan': 'KG', 'netherlands': 'NL', 'kuwait': 'KW', 'denmark': 'DK', 'philippines': 'PH', 'montserrat': 'MS', 'senegal': 'SN', 'tristan da cunha': 'SH', 'congo': 'CG', 'croatia': 'HR', 'bosnia': 'BA', 'chad': 'TD', 'switzerland': 'CH', 'mali': 'ML', 'bulgaria': 'BG', 'jamaica': 'JM', 'albania': 'AL', 'angola': 'AO', 'lebanon': 'LB', 'american samoa': 'AS', 'malaysia': 'MY', 'falkland islands (malvinas)': 'FK', 'christmas island': 'CX', 'mozambique': 'MZ', 'micronesia, federated states of': 'FM', 'greece': 'GR', 'tanzania, united republic of': 'TZ', 'nicaragua': 'NI', 'new zealand': 'NZ', 'brazil': 'BR', 'afghanistan': 'AF', 'qatar': 'QA', 'palau': 'PW', 'turkmenistan': 'TM', 'equatorial guinea': 'GQ', 'pitcairn': 'PN', 'guinea': 'GN', 'panama': 'PA', 'nepal': 'NP', 'central african republic': 'CF', 'luxembourg': 'LU', 'solomon islands': 'SB', 'latvia': 'LV', 'cook islands': 'CK', 'tuvalu': 'TV', 'netherlands antilles': 'AN', 'namibia': 'NA', 'nauru': 'NR', 'russian federation': 'RU', 'british indian ocean territory': 'IO', 'united arab emirates': 'AE', 'south georgia and the south sandwich islands': 'GS', 'saint kitts and nevis': 'KN', 'sri lanka': 'LK', 'paraguay': 'PY', 'china': 'CN', 'armenia': 'AM', 'kiribati': 'KI', 'belize': 'BZ', 'palestinian territory, occupied': 'PS', 'cayman islands': 'KY', 'yemen': 'YE', 'northern mariana islands': 'MP', 'trinidad and tobago': 'TT', 'mayotte': 'YT', 'gambia': 'GM', 'finland': 'FI', 'saint pierre and miquelon': 'PM', 'mauritius': 'MU', 'antigua and barbuda': 'AG', 'niue': 'NU', 'dominican republic': 'DO', "cote d'ivoire": 'CI', 'jersey': 'JE', 'suriname': 'SR', 'pakistan': 'PK', 'romania': 'RO', 'reunion': 'RE', 'czech republic': 'CZ', 'myanmar': 'MM', 'el salvador': 'SV', 'egypt': 'EG', 'guam': 'GU', 'papua new guinea': 'PG', 'united states': 'US', 'austria': 'AT', 'greenland': 'GL', 'colombia': 'CO', 'thailand': 'TH', 'honduras': 'HN', 'niger': 'NE', 'fiji': 'FJ', 'comoros': 'KM', 'turkey': 'TR', 'united kingdom': 'GB', 'madagascar': 'MG', 'iraq': 'IQ', 'bangladesh': 'BD', 'mauritania': 'MR', 'saint barth\xc3\xa9lemy': 'BL', 'uruguay': 'UY', 'france': 'FR', 'bahamas': 'BS', 'slovakia': 'SK', 'gibraltar': 'GI', 'ireland': 'IE', 'nigeria': 'NG', 'anguilla': 'AI', 'malawi': 'MW', 'ecuador': 'EC', 'moldova, republic of': 'MD', 'ukraine': 'UA', 'israel': 'IL', 'congo, the democratic republic of the': 'CD', 'peru': 'PE', 'algeria': 'DZ', 'serbia': 'RS', 'montenegro': 'ME', 'tajikistan': 'TJ', 'svalbard and jan mayen': 'SJ', 'togo': 'TG', 'holy see (vatican city state)': 'VA', 'jordan': 'JO', 'chile': 'CL', 'martinique': 'MQ', 'oman': 'OM', 'turks and caicos islands': 'TC', 'virgin islands, british': 'VG', 'spain': 'ES', 'sao tome and principe': 'ST', 'georgia': 'GE', 'bouvet island': 'BV', 'vietnam': 'VN', 'brunei darussalam': 'BN', 'morocco': 'MA', 'sweden': 'SE', 'heard island and mcdonald islands': 'HM', 'gabon': 'GA', 'guyana': 'GY', 'macedonia, the former yugoslav republic of': 'MK', 'grenada': 'GD', 'guadeloupe': 'GP', 'hong kong': 'HK', 'bahrain': 'BH', "korea, democratic people's republic of": 'KP', 'estonia': 'EE', 'mexico': 'MX', 'india': 'IN', 'new caledonia': 'NC', 'lesotho': 'LS', 'antarctica': 'AQ', 'australia': 'AU', 'saint vincent and the grenadines': 'VC', 'uganda': 'UG', 'burundi': 'BI', 'kenya': 'KE', 'macao': 'MO', 'botswana': 'BW', 'saint martin (french part)': 'MF', 'italy': 'IT', 'western sahara': 'EH', 'south africa': 'ZA', 'cambodia': 'KH', 'ethiopia': 'ET', 'swaziland': 'SZ', 'bermuda': 'BM', 'timor-leste': 'TL', 'vanuatu': 'VU', 'marshall islands': 'MH', 'cameroon': 'CM', 'benin': 'BJ', 'canada': 'CA', "lao, people's democratic republic": 'LA', 'saudi arabia': 'SA', 'singapore': 'SG', 'faroe islands': 'FO', 'iceland': 'IS', 'saint lucia': 'LC', 'monaco': 'MC', 'virgin islands, u.s.': 'VI', 'costa rica': 'CR', 'venezuela': 'VE', 'united states minor outlying islands': 'UM', 'cocos (keeling) islands': 'CC', 'slovenia': 'SI', 'germany': 'DE', '\xc3\x85land islands': 'AX', 'wallis and futuna': 'WF', 'san marino': 'SM', 'dominica': 'DM', 'libyan, arab jamahiriya': 'LY', 'eritrea': 'ER', 'tonga': 'TO', 'maldives': 'MV', 'norfolk island': 'NF', 'poland': 'PL', 'indonesia': 'ID', 'cape verde': 'CV', 'taiwan': 'TW', 'sudan': 'SD', 'liechtenstein': 'LI', 'zimbabwe': 'ZW', 'portugal': 'PT', 'guernsey': 'GG', 'bolivia': 'BO','ascension island': 'AC','east timor': 'TP'}
    c = Country.objects.filter(country__iexact = country.strip().lower())
    c = c[0] if c else ''
    if type == 'random':
        shipping = ShippingManagement.objects.filter(countries=c,gold=False) if c else None
    elif type == 'wholesale':
        shipping = ShippingManagement.objects.filter(countries=c,wholesale=True) if c else None
    else:
        shipping = ShippingManagement.objects.filter(id=type)
    if not shipping:
        shipping = ShippingManagement.objects.filter(countries=c,gold=True) if c else None    
    
    if not shipping:
        raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
   
    if shipping and shipping[0].fixed_shipping:
        return shipping[0].fixed_shipping
    '''---------------------free shipping------------------------'''
    if shipping and shipping[0].free_shipping and orderprice > shipping[0].free_shipping:
        return 'free'
    '''---------------------free shipping------------------------'''
    if shipping[0].api == 'aupost':
        if countries.has_key(country.strip().lower()):
            params = urllib.urlencode({"Quantity":int(quantity),'Service_Type':'AIR','Height':350,'Width':240,'Length':460,'Weight':int(weight),'country':countries[country.strip().lower()],'Destination_Postcode':'2159','Pickup_Postcode':postcode})
            headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
            conn = httplib.HTTPConnection("drc.edeliver.com.au")
            conn.request("POST", "/ratecalc.asp", params, headers)
            response = conn.getresponse()
            data = response.read()
            datas = data.split('\n')
            datass = datas[0].split('=')
            price = float(datass[1])
            if price == 0:
                raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
            else:
                '''------------------------shipping discount--------------'''
                sd = ShippingDiscount.objects.all()
                sd = sd[0] if sd else None
                price = price * sd.getRatio() if sd else price
        
                '''------------------------shipping discount--------------'''
                return price
        else:
            raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)#return calculateshipping(country, postcode, weight)
    elif shipping and shipping[0].api == 'weight':
        baseprice = shipping[0].getBasePrice(weight*quantity)
        if baseprice:
            price = baseprice.amount
        else:
            raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
    elif shipping and shipping[0].api == 'price':
        baseprice = shipping[0].getBasePrice(orderprice)
        if baseprice:
            price = baseprice.amount
        else:
            raise ValueError(settings.TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE)
    else:
        price = None
        
    if price and shipping and shipping[0].minimum_shipping and price < shipping[0].minimum_shipping:
        price = shipping[0].minimum_shipping
    elif price and shipping and shipping[0].maximum_shipping and price > shipping[0].maximum_shipping:
        price = shipping[0].maximum_shipping
    return 'free' if price == 0 else price   
        
    
def getShippingCost(order):
    if not order.is_wholesale:
        try:
            profile = order.user.get_profile()
            shipping = profile.shipping_set.all()[0]
            if shipping.country.country.strip().lower() == 'australia':
                price = postAustralia(getBoxes(order),getBoxWeight(order),shipping.postcode,order.getTotal())
                price = 0.00 if price == 'free' else price
                return eastbourne.helpers.formatCurrency(price)
            else:
                price = postInternational(getBoxes(order), getBoxWeight(order),shipping.postcode, shipping.country.country,order.getTotal())
                price = 0.00 if price == 'free' else price
                return eastbourne.helpers.formatCurrency(price)
        except Exception, e:
                #raise ValueError(e)
                return 13.00
    else:
        return order.shipping_charged

def getBoxes(order):
    weight = order.getTotalWeight()
        
    boxValume = float(35*46*24*0.95)#TO CHANGE
    sum = 0 
    for x in order.productorder_set.all():
        sum = sum + x.getValume()
           
        box = int(math.ceil(sum/boxValume))
        box_least = int(math.ceil(weight/20000.0))
    if box >= box_least:
        return box
    else:
        return box_least

def getTotalPrice(order):
    return eastbourne.helpers.formatCurrency(float(order.getTotalGST())+float(order.getTotalTaxFreePrice())+float(getShippingCost(order)))

def getBoxWeight(order):
    return float(order.getTotalWeight()/getBoxes(order))

def getRandom(number,codes=[]):
    allcodes = []
    coupons = Coupon.objects.all()
    for x in coupons:
        allcodes += x.codes.split(',')
    codes = codes
    for x in xrange(number):
        code = ''.join(random.choice((string.letters+string.digits)) for i in xrange(8))
        while codes.count(code) != 0 or allcodes.count(code) != 0:
            code = ''.join(random.choice((string.letters+string.digits)) for i in xrange(8))
        codes.append(code)
    return ','.join(codes) 

def productOrderSaved(sender, **kwargs):
    po = kwargs["instance"]
    if po.order.user:
        po.order.shipping_charged = float(getShippingCost(po.order))
        po.order.tax_charged = float(po.order.getTotalGST())
        po.order.total_charged = float(getTotalPrice(po.order))
        po.order.save()
        
   

post_save.connect(productOrderSaved, sender=ProductOrder)
post_delete.connect(productOrderSaved, sender=ProductOrder)
