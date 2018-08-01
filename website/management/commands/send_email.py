from django.core.management.base import BaseCommand, CommandError
from eastbourne.website.models import *
import datetime


class Command(BaseCommand):
    help = 'Send email at specified time'
    
    def handle(self, **options):
        now = datetime.datetime.now()
        emails = Email.objects.all()
        for x in emails:
            if x.publish:
                if x.publish.date() == now.date() and x.publish.hour == now.hour and not x.send:
                    x.sendmail()
                    x.send = True
                    x.save()
                    print  '%s is sending' % x.title
                elif x.publish > now:
                    print '%s not sent yet' % x.title
                elif x.publish < now:
                    print '%s has been sent' % x.title