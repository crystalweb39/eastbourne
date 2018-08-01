'''
@author: chaol
'''
import inspect, pprint, string
from eastbourne.userprofile.models import UserLog

class Log:
    def __init__(self, user, message, obj=None):
        pp = pprint.PrettyPrinter(indent=4)
        if obj:
            u = UserLog(user=user, details=message+"\n\n"+pp.pformat(self.props(obj)))
        else:
            u = UserLog(user=user, details=message)
        u.save()
    
    def props(self, obj):
        pr = {}
        for name in dir(obj):
            try:
                value = getattr(obj, name)
                if not name.startswith('_') and (name[0] == name[0].lower()) and not inspect.ismethod(value):
                    pr[name] = value
            except:
                pass
        return pr