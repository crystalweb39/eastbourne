import datetime
from django import template

register = template.Library()

from eastbourne.userprofile.models import Profile

@register.inclusion_tag('admin/userprofile/profile/toplinks.html')
def display_toplinks(document_id):
    profile = Profile.objects.get(id__exact=document_id)
    user = profile.user
    return { 'usr': user }
