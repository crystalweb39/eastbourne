#! /bin/bash
python manage.py dumpdata auth > fixtures/auth.json
python manage.py dumpdata sites > fixtures/sites.json
python manage.py dumpdata blog > fixtures/blog.json
python manage.py dumpdata website > fixtures/website.json
python manage.py dumpdata shop > fixtures/shop.json
python manage.py dumpdata userprofile > fixtures/userprofile.json
python manage.py dumpdata stockists > fixtures/stockists.json
svn ci -m "Dumping fixture data from the live site"
