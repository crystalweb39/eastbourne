'''
@author: chaol
'''

from django.db import models
from django.core.validators import email_re
from eastbourne.blog.models import PublishStatus
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def is_valid_email(email):
    return True if email_re.match(email) else False

class MiscPage(models.Model):
    title = models.CharField(max_length=255)
    path = models.CharField(max_length=255, help_text="eg. /about/")
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(PublishStatus)
    header = models.ImageField(upload_to="images/")
    def __unicode__(self):
        return self.title
class NewsItem(models.Model):
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    publish_date = models.DateTimeField()
    url = models.URLField(blank=True, null=True)
    status = models.ForeignKey(PublishStatus)
    def __unicode__(self):
        return self.title
class Stockist(models.Model):
    suburb = models.CharField(max_length=60)
    shop_name = models.CharField(max_length=60)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=6)
    phone = models.CharField(max_length=20)
    def __unicode__(self):
        return self.shop_name
class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.DateTimeField(auto_now_add=True)
    is_wholesale = models.BooleanField(default=False)
    ip = models.CharField(max_length=20, null=True, blank=True)
    stamp = models.DateTimeField(auto_now_add=True)
    
 
    def __unicode__(self):
        return self.email
    
    def email_not_read(self):
        emails = self.emailstatus_set.filter(read=False)
        return ','.join([x.email.title for x in emails])
    
    class Meta:
        ordering = ('email',)
class Strings(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    text = models.CharField(max_length=255)
    def __unicode__(self):
        return self.identifier
    
class FlashPage(models.Model):
    path = models.CharField(max_length=60)
    def __unicode__(self):
        return self.path
    
class FlashImage(models.Model):
    flash = models.ForeignKey(FlashPage)
    image = models.FileField(upload_to="images/")
    in_flash = models.BooleanField(default=False)
    in_js = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    link = models.URLField(blank=True,null=True)
    priority = models.IntegerField(default=0)
    def __unicode__(self):
        return self.flash.path
    
class Email(models.Model):
    title = models.CharField(max_length=255,unique=True)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    publish = models.DateTimeField(editable=False,blank=True,null=True)
    send = models.BooleanField(default=False,editable=False)
    def __unicode__(self):
        return self.title
    
    def send_already(self):
        return True if self.send else False
    
    def read_percentage(self):
        all = self.emailstatus_set.all()
        all = len(all)
        read = self.emailstatus_set.filter(read=True)
        read = len(read)
        return '%s/%s' %(read,all) 
    
    def not_read_percentage(self):
        all = self.emailstatus_set.all()
        all = len(all)
        notread = self.emailstatus_set.filter(read=False)
        notread = len(notread)
        return '%s/%s' %(notread,all) 
        
    def sendmail(self,subscribe=''):
        domain = settings.DOMAIN

        for x in subscribe:
            if is_valid_email(x.email):
                try:
                    content = "%s <br /> <img src='http://%s/reademail?id=%s&email=%s' width='1' height='1' />" %(self.content, domain, x.id, self.id)
                    email = EmailMultiAlternatives(self.title , content, 'Eastbourne Art <contact@eastbourneart.com.au>', [x.email])
                    email.attach_alternative(content, "text/html")
                    email.send()
                    es = x.emailstatus_set.filter(email = self)
                    if not es:
                        es = EmailStatus()
                        es.email = self
                        es.subscribe = x
                        es.save()
                except:
                    pass
                
            
class EmailStatus(models.Model):
    email = models.ForeignKey(Email)
    subscribe = models.ForeignKey(Subscription)
    read = models.BooleanField(default=False,editable=False)
    def __unicode__(self):
        return self.email.title

#def EmailSaved(sender, **kwargs):
#    email = kwargs["instance"]
#    s = Subscription.objects.all()
    
#    for x in s:
#        es = x.emailstatus_set.filter(email = email)
#        if not es:
#            es = EmailStatus()
#            es.email = email
#            es.subscribe = x
#            es.save()
  
#post_save.connect(EmailSaved, sender=Email)

    