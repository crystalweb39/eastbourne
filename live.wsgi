import os
import sys
import site

path = '/home/chaol/projects/'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'eastbourne.settings-custom'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

