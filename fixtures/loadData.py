from django.core import management
management.call_command('loaddata', 'auth.json', verbosity=1)
management.call_command('loaddata', 'sites.json', verbosity=1)
management.call_command('loaddata', 'blog.json', verbosity=1)
management.call_command('loaddata', 'stockists.json', verbosity=1)
management.call_command('loaddata', 'userprofile.json', verbosity=1)
management.call_command('loaddata', 'website.json', verbosity=1)
management.call_command('loaddata', 'shop.json', verbosity=1)
management.call_command('syncdb', verbosity=1)