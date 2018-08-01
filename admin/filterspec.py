from django.db import models
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec, BooleanFieldFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from eastbourne.shop.models import *

class WholesaleFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        super(WholesaleFilterSpec, self).__init__(f, request, params, model, model_admin, *args, **kwargs)
        self.lookup_kwarg = 'profile__wholesale'
        self.lookup_kwarg2 = 'profile__wholesale'
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        # disabled this so that the items will be selected (look down a little), could be done better
        self.lookup_val2 = None#request.GET.get(self.lookup_kwarg2, None)

    def title(self):
        return "Wholesale"

    def choices(self, cl):
        for k, v in ((_('All'), None), (_('Yes'), '1'), (_('No'), '0')):
            yield {'selected': self.lookup_val == v and not self.lookup_val2,
                   'query_string': cl.get_query_string({self.lookup_kwarg: v}, [self.lookup_kwarg2]),
                   'display': k}
        if isinstance(self.field, models.NullBooleanField):
            yield {'selected': self.lookup_val2 == 'True',
                   'query_string': cl.get_query_string({self.lookup_kwarg2: 'True'}, [self.lookup_kwarg]),
                   'display': _('Unknown')}
FilterSpec.filter_specs.insert(0,
  # If the field has a `profilecountry_filter` attribute set to True
  # the this FilterSpec will be used
  (lambda f: getattr(f, 'wholesale_filter', False), WholesaleFilterSpec)
)
'''---------------------------------MY FILTER----------------------------------'''
class CouponFilterSpec(ChoicesFilterSpec):
    def __init__(self, f, request, params, model, model_admin,*args, **kwargs):
        ChoicesFilterSpec.__init__(self, f, request, params, model, model_admin, *args, **kwargs)
        self.lookup_kwarg = 'coupon__name'
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        
        coupon_qs = Coupon.objects.all()
        self.lookup_choices = coupon_qs.values_list('name', flat=True)
        
        
    def choices(self,cl):
        yield { 'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All') }
        for val in self.lookup_choices:
            yield { 'selected' : smart_unicode(val) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                    'display': val }

    def title(self):
        # return the title displayed above your filter
        return _('coupon')
    
FilterSpec.filter_specs.insert(0,
  # If the field has a `profilecountry_filter` attribute set to True
  # the this FilterSpec will be used
  (lambda f: getattr(f, 'coupon_filter', False), CouponFilterSpec)
)

class CategoryFilterSpec(ChoicesFilterSpec):
    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        ChoicesFilterSpec.__init__(self, f, request, params, model, model_admin, *args, **kwargs)
        self.lookup_kwarg = 'product__category_now__name'
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        coupon_qs = Categories.objects.all().order_by('-parent','-name')
        self.lookup_choices = coupon_qs.values_list('name', flat=True)
        
        
    def choices(self,cl):
        yield { 'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All') }
        for val in self.lookup_choices:
            yield { 'selected' : smart_unicode(val) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                    'display': val }

    def title(self):
        # return the title displayed above your filter
        return _('category')
    
FilterSpec.filter_specs.insert(0,
  # If the field has a `profilecountry_filter` attribute set to True
  # the this FilterSpec will be used
  (lambda f: getattr(f, 'category_filter', False), CategoryFilterSpec)
)


class InCouponFilterSpec(BooleanFieldFilterSpec):
    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        BooleanFieldFilterSpec.__init__(self, f, request, params, model, model_admin, *args, **kwargs)
        self.lookup_kwarg = 'coupon__isnull'
        self.lookup_kwarg2 = 'coupon__exact'
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val2 = None
        
    
    def title(self):
        return 'in coupon'

    def choices(self, cl):
        for k, v in ((_('All'), None), (_('No'), 'True')):
            yield {'selected': self.lookup_val == v and not self.lookup_val2,
                   'query_string': cl.get_query_string({self.lookup_kwarg: v}, [self.lookup_kwarg2]),
                   'display': k}
        if isinstance(self.field, models.NullBooleanField):
            yield {'selected': self.lookup_val2 == 'True',
                   'query_string': cl.get_query_string({self.lookup_kwarg2: 'True'}, [self.lookup_kwarg]),
                   'display': _('Unknown')}

FilterSpec.filter_specs.insert(0,
  # If the field has a `profilecountry_filter` attribute set to True
  # the this FilterSpec will be used
  (lambda f: getattr(f, 'in_coupon_filter', False), InCouponFilterSpec)
)
'''---------------------------------MY FILTER----------------------------------'''


#FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'company_filter', False), CompanyFilterSpec))
#
#class AlphabeticFilterSpec(ChoicesFilterSpec):
#    """
#    Adds filtering by first char (alphabetic style) of values in the admin
#    filter sidebar. Set the alphabetic filter in the model field attribute
#    'alphabetic_filter'.
#
#    my_model_field.alphabetic_filter = True
#    """
#
#    def __init__(self, f, request, params, model, model_admin):
#        super(AlphabeticFilterSpec, self).__init__(f, request, params, model, model_admin)
#        self.lookup_kwarg = 'user__username__istartswith'
#        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
#        values_list = model.objects.values_list(f.name, flat=True)
#        # getting the first char of values
#        self.lookup_choices = list(set(val[0] for val in values_list if val))
#        self.lookup_choices.sort()
#
#    def choices(self, cl):
#        yield {'selected': self.lookup_val is None,
#                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
#                'display': _('All')}
#        for val in self.lookup_choices:
#            yield {'selected': smart_unicode(val) == self.lookup_val,
#                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
#                    'display': val.upper()}
#    def title(self):
#        return _('%(field_name)s that starts with') % {'field_name': self.field.verbose_name}
#
## registering the filter
#FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'alphabetic_filter', False), AlphabeticFilterSpec))
