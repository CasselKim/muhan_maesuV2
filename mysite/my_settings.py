#MUHAN_ADMIN_PAGE>mysite>my_settings.py

import sys
import json
import os

# get secret key from json file
secrets = json.loads(open('secret.json').read())

# create and allocate value : password 
for key, value in secrets.items():
    setattr(sys.modules[__name__], key, value)

# set password
DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : 'muhan_db',
        'USER' : 'guest',
        'PASSWORD' : PASSWORD,
        'HOST' : 'localhost',
        'PORT' : '3306',
    }
}