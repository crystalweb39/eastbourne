"""Default variable filters."""

import re

try:
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
except ImportError:
    from django.utils._decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import random as random_module
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.template import Variable, Library
from django.conf import settings
from django.utils.translation import ugettext, ungettext
from django.utils.encoding import force_unicode, iri_to_uri
from django.utils.safestring import mark_safe, SafeData

register = Library()

def inlist(value, arg):
    if not value:
        return False
    return bool(value.count(arg) > 0)

register.filter(inlist)
def islast(value, arg):
    if not value:
        return False
    return bool(value[len(value)-1] == arg)

register.filter(islast)
