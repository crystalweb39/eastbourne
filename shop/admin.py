'''
@author: chaol
'''
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site

from eastbourne.shop.models import *
from django.forms.models import BaseInlineFormSet
class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

class CountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'shipto',)
    list_filter = ('shipto',)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country',)
    list_filter = ('country',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage

class ProductOrderInline(admin.TabularInline):
    model = ProductOrder
   # template = 'admin/shop/order/inline.html'
    readonly_fields = ('__unicode__','coupon')

class ProductOrderAdmin(admin.ModelAdmin):
    
    list_display=('order','product', 'getCategory', 'quantity', 'getOrderStatus',)
    list_filter=('size','style',)
    search_fields =('product','size','style')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('getOrderNumber', 'user_detail', 'status', 'is_wholesale','shipping_charged','tax_charged','getTotalCharged', 'getTotalItems', 'coupon_used','started', 'updated')
   
    list_filter = ('status', 'is_wholesale', 'started', 'updated',)
    inlines = [
        ProductOrderInline
    ]
    #readonly_fields = ('user','is_wholesale','shipping_charged','tax_charged','total_charged')
    
    '''def get_form(self, request, obj=None, **kwargs):
        form = super(OrderAdmin,self).get_form(self,request,**kwargs)
        # form class is created per request by modelform_factory function
        # so it's safe to modify
        #we modify the the queryset
        form.base_fields['status'].queryset = OrderStatus.objects.exclude(status='In Progress')
        return form'''
    
    def queryset(self, request):
        #form.status.queryset = OrderStatus.objects.exclude(status="In Progress")
       
        return super(OrderAdmin,self).queryset(request).exclude(status__status="In Progress",is_wholesale=False)

class DiscountPriceInline(admin.TabularInline):
    model = DiscountPrice.coupon.through
    extra = 0

class ProductSizePriceInline(admin.TabularInline):
    model = ProductSizePrice
    
class DiscountedPriceSizeInline(admin.TabularInline):
    model = DiscountedPriceSize

class DiscountPriceAdmin(admin.ModelAdmin):
    list_display=('product','start','end','getCategory','priceoff','wholesale_priceoff','coupon_name')
    search_fields=('product',)
    
    inlines = [DiscountPriceInline,]
    exclude = ('coupon',)
    actions =['add_to_coupon']
    DiscountPrice._meta.get_field('coupon').coupon_filter = True
    DiscountPrice._meta.get_field('price').in_coupon_filter = True
    #DiscountPrice._meta.get_field('product').category_filter = True
    list_filter=('start','end','coupon','price')
    #inlines = [ DiscountedPriceSizeInline, ]
    def add_to_coupon(self,request,queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect('addtocoupon/?ids=%s' % ",".join(selected))

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"code": ("title",)}
    list_display = ('title', 'code', 'getCategory', 'weight', 'height', 'length', 'width','status','inventory')
    
    list_filter = ('category_now','status')
    search_fields = ('code','title','description')
    list_editable = ('weight','height', 'length', 'width','status','inventory')
    inlines = [
        ProductImageInline,ProductSizePriceInline,
    ]
    actions = ['add_to_discountprice','add_to_category']
    def add_to_category(self,request,queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect('addtocategory/?ids=%s' % ",".join(selected))
        
        
class CategoryAdmin(admin.ModelAdmin):
    fields = ("parent", "name", "slug", "image", "priority", "is_active")
    list_display = ("name", "parent", "priority", "is_active")
    list_filter = ("is_active", 'parent', "priority", )
    prepopulated_fields = {"slug": ("name",)}

class CategoriesAdmin(admin.ModelAdmin):
    fields = ("parent", "name", "slug", "image", "priority", "is_active")
    list_display = ("name", "parent", "priority", "is_active")
    list_filter = ("is_active", 'parent', "priority", )
    prepopulated_fields = {"slug": ("name",)}

    
class ProductSizePriceAdmin(admin.ModelAdmin):
    list_display = ('product','size','price','wholesale_price')
    list_filter = ('product', 'size')
    search_fields = ('product','size')



class CouponAdmin(admin.ModelAdmin):
    list_display= ('name','codes',)
    inlines = [DiscountPriceInline,]
    #__name__ = 'discountprice_set'
    
class ShippingDiscountAdmin(admin.ModelAdmin):
    list_display=('name','off')
    list_editable=('off',)


class ShippingBasedInline(admin.TabularInline):
    model = ShippingBased
    extra = 0
    formset = RequiredInlineFormSet
    
class ShippingManagementAdmin(admin.ModelAdmin):
    inlines = [ShippingBasedInline,]
    list_display = ('name','api','fixed_shipping','gold','display_countries')
    list_editable = ('api','fixed_shipping')
    list_filter = ('countries',)
    
    '''def get_form(self,request, obj=None, **kwargs):
        form = super(ShippingManagementAdmin,self).get_form(request, **kwargs)
        if not obj:
            sm = ShippingManagement.objects.all()
            cs = []
            for x in sm:
                cs += x.countries.all()
                
            form.base_fields['countries'].queryset = Country.objects.exclude(country__in=cs)
        return form'''

#admin.site.register(Category, CategoryAdmin)
admin.site.register(TaxRate)
#admin.site.register(ShippingDiscount,ShippingDiscountAdmin)
admin.site.register(Size)
admin.site.register(Style)
admin.site.register(ProductStatus)
admin.site.register(Product, ProductAdmin)
admin.site.register(PackageProduct)
admin.site.register(DiscountPrice,DiscountPriceAdmin)
admin.site.register(OrderStatus)
admin.site.register(ProductOrder, ProductOrderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Categories,CategoriesAdmin)
admin.site.register(Coupon,CouponAdmin)
admin.site.register(ShippingManagement,ShippingManagementAdmin)
#admin.site.register(ProductSizePrice, ProductSizePriceAdmin)



from django.contrib.auth.admin import UserAdmin as DJUserAdmin
from eastbourne.admin import filterspec
from django.db import connection
admin.site.unregister(User)




class RetailUserAdmin(DJUserAdmin):
    model = User
    #User._meta.get_field('username').wholesale_filter = True
    #User._meta.get_field('first_name').company_filter = True
    list_display = ['username', 'first_name', 'last_name', 'is_active', 'is_staff', 'last_login']
    list_filter = ['profile__wholesale', 'is_active', 'is_staff']
    list_editable = ['is_active', 'is_staff']

#    def queryset(self, request):
#        raise ValueError(str(dir(User.objects.filter()[0])))
#        qs = super(RetailUserAdmin, self).queryset(request).exclude(username__startswith="retail")
#        if request.GET.get("username__istartswith", "").lower() == "retail_":
#            qs.filter(username__istartswith="retail_")
#        if int(request.GET.get("is_active__exact", 1)) == 0:
#            pass
#        qs.exclude(username__startswith="retail")
#        #return ValueError(connection.queries)
#        return qs

admin.site.register(User, RetailUserAdmin)
