import os
from ahe_project.settings_base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('AHE_DB_NAME', 'ahe_log'),
        'USER': os.getenv('AHE_DB_USER', 'ahe_log'),
        'PASSWORD': os.getenv('AHE_DB_PASSWORD', 'ahe_log'),
        'HOST': os.getenv('AHE_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('AHE_DB_PORT', '3306'),
        'TEST': {
            'NAME': f"test_{os.getenv('DB_NAME')}",
        }
    }
}
