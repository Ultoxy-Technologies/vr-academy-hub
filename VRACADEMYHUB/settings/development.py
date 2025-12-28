from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Razorpay TEST keys
RAZORPAY_KEY_ID = 'rzp_test_RfELpk3eZdngJZ'
RAZORPAY_KEY_SECRET = 'lWVYlpQE8ftiRcrmfv1M8arF'

# Email (optional: console backend for dev)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
