from .base import *

#Development settings
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}