import datetime
from django import template

register = template.Library()
from django.template import Variable, Library,Node,NodeList,resolve_variable
from eastbourne.shop.models import Product




@register.tag(name="display_current_price")
def do_display_current_price(parser,token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise 
    return DisplayCurrentPrice(bits[1], bits[2], bits[3],bits[4])

class DisplayCurrentPrice(template.Node):
    def __init__(self,product,wholesale,coupon,display):
        self.product, self.wholesale, self.coupon,self.display = product,wholesale,coupon,display
    
    def render(self,context):
        product = resolve_variable(self.product, context)
        coupon = resolve_variable(self.coupon, context)
        wholesale = resolve_variable(self.wholesale, context)
        wholesale = True if wholesale else False
        price = product.getCurrentRightPrice('',wholesale,coupon)
        if self.display == 'price':
            return "AU$"+price
        elif self.display == 'comboprice':
            if product.productsizeprice_set.all():
                return '''<div class="price">AU$<span id='price'>%s</span></div>''' % product.getFirstPrice(wholesale,coupon)
            else:
                return '''<div class="price">AU$%s</div>''' % price
            
        else:
            if price != product.getNormalPrice(wholesale):
                return '''<strike>$AU %s </strike><br/>
                       <strong class="discounted">$AU %s </strong></a>''' %(product.getNormalPrice(wholesale), price)
            else:
                return '''<strong>$AU %s</strong></a>''' % price
        
        
@register.tag(name="current_time")
def do_current_time(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return CurrentTimeNode(format_string[1:-1])

class CurrentTimeNode(template.Node):
    def __init__(self, format_string):
        self.format_string = format_string
    def render(self, context):
        return str((context.dicts[1]))
        return datetime.datetime.now().strftime(self.format_string)

@register.tag(name="category_display_price")
def do_category_display_price(parser, args):
    return CategoryCurrentPriceNode()

class CategoryCurrentPriceNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        if context.dicts[3].has_key("user"):
            price = str(((context.dicts[0]['x']).getTaxPrice(True)))
        else:
            price = str(((context.dicts[0]['x']).getTaxPrice(False)))
        if not context.dicts[0]['x'].isDiscounted(context.dicts[3].has_key("user")):
            return """<strong>$AU %s (inc.GST)</strong>""" % price
        else:
            normalPrice = str(((context.dicts[0]['x']).getNormalTaxPrice(context.dicts[3].has_key("user"))))
            return """<strike>$AU %s (inc.GST)</strike><br/><strong class="discounted">$AU %s (inc.GST)</strong>""" % (normalPrice, price)
@register.tag(name="product_display_price")
def do_product_display_price(parser, args):
    return ProductCurrentPriceNode()

class ProductCurrentPriceNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        if context.dicts[3].has_key("user"):
            price = str(((context.dicts[0]['x']).getTaxPrice(True)))
        else:
            price = str(((context.dicts[0]['x']).getTaxPrice(False)))
        if not context.dicts[0]['x'].isDiscounted(context.dicts[3].has_key("user")):
            return """<strong>$AU %s (inc.GST)</strong>""" % price
        else:
            normalPrice = str(((context.dicts[0]['x']).getNormalTaxPrice(context.dicts[3].has_key("user"))))
            return """<strike>$AU %s (inc.GST)</strike><br/><strong class="discounted">$AU %s (inc.GST)</strong>""" % (normalPrice, price)
