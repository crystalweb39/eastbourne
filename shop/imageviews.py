'''
@author: chaol
'''

from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout
from django.conf import settings
import datetime, time
from models import *
from django.db import connection
import os
from operator import itemgetter

def imager(request, path, w, h, crop=1):
    crop = str(crop)
    try:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, "zoom", w, h, crop, path)):
            return HttpResponseRedirect(os.path.join("/media/zoom", w, h, crop, path))
    except Exception, e:
        return HttpResponse(str(e))
    try:
        import Image, ImageOps
        size = int(w), int(h)
        centering = 0.5, 0.5
        img = Image.open(os.path.join(settings.MEDIA_ROOT, path))
        if int(crop) > 0:
            img = ImageOps.fit(img, size, Image.ANTIALIAS, 0, centering)
            #img = img.resize(size, Image.ANTIALIAS) 
        else:
            img.thumbnail(size, Image.ANTIALIAS)
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, "zoom", w, h, crop, "/".join(os.path.split(path)[:-1])))
        except:
            pass
        img.save(os.path.join(settings.MEDIA_ROOT, "zoom", w, h, crop, path), quality=90, optimize=True)
        return HttpResponseRedirect(os.path.join("/media/zoom", w, h, crop, path))
    except Exception, e:
        return HttpResponse(str(e))
