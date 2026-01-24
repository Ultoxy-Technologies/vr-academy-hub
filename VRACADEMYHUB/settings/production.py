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

# Production api keys
RAZORPAY_KEY_ID = 'rzp_live_S0GtEF2P4Jr7SY' 
#Production api secret keys
RAZORPAY_KEY_SECRET = 'RLFz6G1j9CgStlwKDFyBIqPK'



# Razorpay LIVE keys
# #test api keys
# RAZORPAY_KEY_ID = 'rzp_live_S0GtEF2P4Jr7SY' 
# #test api secret keys
# RAZORPAY_KEY_SECRET = 'RLFz6G1j9CgStlwKDFyBIqPK'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'vrtrainingacademy@gmail.com'
EMAIL_HOST_PASSWORD = 'lawo tafh hxwd bqok'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

# Production URLs
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Production filesystem paths
STATIC_ROOT = '/var/www/vracademyhub_static'
MEDIA_ROOT = '/var/www/vracademyhub_media'


# Timezone settings for India
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True


LANGUAGE_CODE = 'en-in'  # English for India
USE_I18N = True
USE_L10N = True

USE_L10N = False 


import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'file': {
            'level': 'ERROR',   # log only ERROR and CRITICAL
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'formatter': 'verbose',
        },
    },

    'loggers': {
        # Django internal errors
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },

        # Catch errors from your apps
        '': {  # root logger
            'handlers': ['file'],
            'level': 'ERROR',
        },
    },
}
