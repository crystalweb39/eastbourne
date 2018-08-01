'''
@author: chaol
'''

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.http import HttpResponseRedirect
from models import *

class MiscPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created',)
    list_filter = ('created', 'modified', 'status')
    class Media:
        js = ['/media/adminmedia/tinymce/jscripts/tiny_mce/tiny_mce.js', '/media/adminmedia/tinymce_setup/tinymce_setup.js',]
class StringsAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'text',)
    search_fields = ('identifier', 'text')
    
class EmailStatusInline(admin.TabularInline):
    model = EmailStatus    

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email','subscribed','is_wholesale','ip','email_not_read')
    list_filter = ('subscribed','is_wholesale',)
    search_fields = ('email',)
    inlines = [EmailStatusInline,]
    actions = ['send_mail']
    list_per_page = 2147483647
    def send_mail(self,request,queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect('sendmail/?ids=%s' % ",".join(selected))
        
    
class FlashImageInline(admin.TabularInline):
    model = FlashImage

class FlashPageAdmin(admin.ModelAdmin):
    inlines = [FlashImageInline,]
    
class EmailAdmin(admin.ModelAdmin):
    list_display=('title','created','send_already','read_percentage','not_read_percentage')
    list_filter=('created',)

    actions = ['duplicate_email']
    
    def duplicate_email(self,request,queryset):
        content = ''
        titles = []
        for x in queryset:
            titles.append(x.title)
            content += x.content
        e = Email()
        num = 0
        title = 'please_change_me'
        while title in titles:
            num += 1
            titlelist = title.split('_')[:3]
            titlelist.append(str(num))
            title = '_'.join(titlelist)
            
            
        e.title = title
        e.content = content
        e.save()
        return HttpResponseRedirect('/admin/website/email/')
        
        
    
    #class Media:
    #    js = ['/media/adminmedia/tinymce/jscripts/tiny_mce/tiny_mce.js', '/media/adminmedia/tinymce_setup/tinymce_setup.js',]
    

    

admin.site.register(MiscPage, MiscPageAdmin)
admin.site.register(NewsItem)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Strings, StringsAdmin)
admin.site.register(FlashPage,FlashPageAdmin)
admin.site.register(Email,EmailAdmin)