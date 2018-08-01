'''
@author: chaol
'''

from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms
from django.core.urlresolvers import reverse

from models import *

class BlogPostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'status', 'publishdate',)
    list_filter = ('created', 'modified', 'status')
    class Media:
        js = ['/media/adminmedia/tinymce/jscripts/tiny_mce/tiny_mce.js', '/media/adminmedia/tinymce_setup/tinymce_setup.js',]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'email', 'created',)
    list_filter = ('created', 'status', 'created')

#admin.site.unregister(BlogPost)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PublishStatus)
admin.site.register(CommentStatus)