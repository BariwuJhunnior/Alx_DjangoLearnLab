from .base import *

DEBUG = True

ALLOWED_HOSTS = []

import os
import dj_database_url

# Example configuration reading from environment variable
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}

# 3. Static and Media Files (Crucial for Deployment)
# Where collected static files will live
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 4. HTTPS and Security Headers
# Assumes you are running behind a reverse proxy (like Nginx/Gunicorn) that handles SSL/TLS
# If your deployment enforces HTTPS (highly recommended):

# Redirect all HTTP requests to HTTPS (requires configuring your web server too)
SECURE_SSL_REDIRECT = True 
# Helps prevent Man-in-the-Middle attacks 
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Protects against cross-site scripting (XSS)
SECURE_BROWSER_XSS_FILTER = True
# Prevents the browser from guessing the MIME type of content
SECURE_CONTENT_TYPE_NOSNIFF = True

# Prevents clickjacking attacks (default is 'DENY' in newer Django, but setting explicitly is safer)
X_FRAME_OPTIONS = 'DENY'

# Setting this to True prevents the browser from sending the CSRF token cookie 
# with cross-site requests (protects against CSRF attacks)
CSRF_COOKIE_SECURE = True
# Setting this to True ensures the session cookie is only transmitted over HTTPS
SESSION_COOKIE_SECURE = True

# 5. Logging (Essential for debugging production issues)
# You must set up proper logging to a file or a service (like Sentry/CloudWatch)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/production_warnings.log', # CHANGE PATH AS NEEDED
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}