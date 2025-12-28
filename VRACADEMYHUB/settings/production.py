from .base import *

DEBUG = False

ALLOWED_HOSTS = ['vracademyhub.com',
    'www.vracademyhub.com',
    '72.60.96.41',
    'localhost',
    '127.0.0.1',]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # or PostgreSQL later
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Razorpay LIVE keys
RAZORPAY_KEY_ID = 'rzp_live_xxxxx'
RAZORPAY_KEY_SECRET = 'live_secret_xxxxx'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'vrtrainingacademy@gmail.com'
EMAIL_HOST_PASSWORD = 'APP_PASSWORD'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Production URLs
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Production filesystem paths
STATIC_ROOT = '/var/www/vracademyhub_static'
MEDIA_ROOT = '/var/www/vracademyhub_media'